"""
Módulo de Gerenciamento de RAG (Retrieval-Augmented Generation)
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Este módulo gerencia o pipeline de ingestion, embedding e retrieval
de documentos para aumentação de contexto em análises.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import json


class TipoDocumento(str, Enum):
    """Tipos de documentos no RAG."""
    TECNICO = "técnico"
    NORMATIVO = "normativo"
    REGULAMENTACAO = "regulamentação"
    PARECER = "parecer"
    PROCEDIMENTO = "procedimento"
    REFERENCIA = "referência"


class StatusIngestion(str, Enum):
    """Status de ingestion de documento."""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    INDEXADO = "indexado"
    ERRO = "erro"


@dataclass
class Documento:
    """Documento no RAG."""
    id: str
    titulo: str
    tipo: TipoDocumento
    conteudo: str
    fonte: str
    data_criacao: datetime
    data_atualizacao: datetime
    tags: List[str] = field(default_factory=list)
    metadados: Dict[str, Any] = field(default_factory=dict)
    hash_conteudo: str = ""


@dataclass
class Chunk:
    """Fragmento de documento para embedding."""
    id: str
    documento_id: str
    conteudo: str
    numero_sequencia: int
    embedding: Optional[List[float]] = None
    metadados: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultadoBusca:
    """Resultado de busca no RAG."""
    chunks: List[Chunk]
    scores_similaridade: List[float]
    documentos_relacionados: List[Documento]
    tempo_busca_ms: float
    total_resultados: int


class GerenciadorRAG:
    """
    Gerenciador de RAG determinístico.
    Implementa pipeline de ingestion, indexação e retrieval.
    """

    # Configurações
    TAMANHO_CHUNK = 512  # tokens
    SOBREPOSICAO_CHUNK = 50  # tokens
    LIMITE_RESULTADOS = 5
    LIMITE_SIMILARIDADE = 0.3

    def __init__(self):
        """Inicializa o gerenciador."""
        self.documentos: Dict[str, Documento] = {}
        self.chunks: Dict[str, Chunk] = {}
        self.indice_busca: Dict[str, List[str]] = {}  # palavra-chave -> chunk_ids
        self.historico_ingestion: List[Dict[str, Any]] = []
        self.historico_busca: List[ResultadoBusca] = []

    def ingerir_documento(
        self,
        titulo: str,
        conteudo: str,
        tipo: TipoDocumento,
        fonte: str,
        tags: Optional[List[str]] = None,
        metadados: Optional[Dict[str, Any]] = None,
    ) -> Documento:
        """
        Ingere um novo documento no RAG.

        Args:
            titulo: Título do documento
            conteudo: Conteúdo do documento
            tipo: Tipo de documento
            fonte: Fonte/origem do documento
            tags: Tags para classificação
            metadados: Metadados adicionais

        Returns:
            Documento criado
        """
        # Gerar ID e hash
        doc_id = self._gerar_id_documento(titulo, fonte)
        hash_conteudo = self._calcular_hash(conteudo)

        # Verificar duplicação
        if doc_id in self.documentos:
            doc_existente = self.documentos[doc_id]
            if doc_existente.hash_conteudo == hash_conteudo:
                return doc_existente
            # Atualizar documento existente
            doc_existente.conteudo = conteudo
            doc_existente.data_atualizacao = datetime.utcnow()
            doc_existente.hash_conteudo = hash_conteudo
            self._fragmentar_documento(doc_existente)
            return doc_existente

        # Criar novo documento
        documento = Documento(
            id=doc_id,
            titulo=titulo,
            tipo=tipo,
            conteudo=conteudo,
            fonte=fonte,
            data_criacao=datetime.utcnow(),
            data_atualizacao=datetime.utcnow(),
            tags=tags or [],
            metadados=metadados or {},
            hash_conteudo=hash_conteudo,
        )

        self.documentos[doc_id] = documento

        # Fragmentar e indexar
        self._fragmentar_documento(documento)
        self._indexar_documento(documento)

        # Registrar ingestion
        self.historico_ingestion.append({
            "documento_id": doc_id,
            "titulo": titulo,
            "tipo": tipo.value,
            "status": StatusIngestion.INDEXADO.value,
            "timestamp": datetime.utcnow().isoformat(),
            "tamanho_bytes": len(conteudo.encode('utf-8')),
            "total_chunks": len([c for c in self.chunks.values() if c.documento_id == doc_id]),
        })

        return documento

    def _fragmentar_documento(self, documento: Documento) -> List[Chunk]:
        """
        Fragmenta documento em chunks.

        Args:
            documento: Documento a fragmentar

        Returns:
            Lista de chunks criados
        """
        chunks_criados = []
        conteudo = documento.conteudo
        palavras = conteudo.split()

        # Remover chunks antigos
        chunks_antigos = [
            c for c in self.chunks.values()
            if c.documento_id == documento.id
        ]
        for chunk_antigo in chunks_antigos:
            del self.chunks[chunk_antigo.id]

        # Criar novos chunks
        for i in range(0, len(palavras), self.TAMANHO_CHUNK - self.SOBREPOSICAO_CHUNK):
            fim = min(i + self.TAMANHO_CHUNK, len(palavras))
            conteudo_chunk = " ".join(palavras[i:fim])

            chunk_id = f"{documento.id}_chunk_{len(chunks_criados)}"
            chunk = Chunk(
                id=chunk_id,
                documento_id=documento.id,
                conteudo=conteudo_chunk,
                numero_sequencia=len(chunks_criados),
                metadados={
                    "tipo_documento": documento.tipo.value,
                    "fonte": documento.fonte,
                    "tags": documento.tags,
                },
            )

            self.chunks[chunk_id] = chunk
            chunks_criados.append(chunk)

        return chunks_criados

    def _indexar_documento(self, documento: Documento) -> None:
        """
        Indexa documento para busca.

        Args:
            documento: Documento a indexar
        """
        # Extrair palavras-chave
        palavras_chave = self._extrair_palavras_chave(documento.conteudo)

        # Indexar cada palavra-chave
        for palavra in palavras_chave:
            if palavra not in self.indice_busca:
                self.indice_busca[palavra] = []

            # Adicionar chunks deste documento
            chunks_doc = [
                c.id for c in self.chunks.values()
                if c.documento_id == documento.id
            ]
            self.indice_busca[palavra].extend(chunks_doc)

    def buscar(
        self,
        query: str,
        tipo_documento: Optional[TipoDocumento] = None,
        limite: Optional[int] = None,
    ) -> ResultadoBusca:
        """
        Busca documentos no RAG.

        Args:
            query: Consulta de busca
            tipo_documento: Filtrar por tipo (opcional)
            limite: Limite de resultados

        Returns:
            ResultadoBusca com chunks relevantes
        """
        import time
        tempo_inicio = time.time()

        if limite is None:
            limite = self.LIMITE_RESULTADOS

        # Extrair palavras-chave da query
        palavras_query = self._extrair_palavras_chave(query)

        # Buscar chunks relevantes
        chunks_relevantes: Dict[str, float] = {}

        for palavra in palavras_query:
            if palavra in self.indice_busca:
                for chunk_id in self.indice_busca[palavra]:
                    if chunk_id not in chunks_relevantes:
                        chunks_relevantes[chunk_id] = 0.0
                    chunks_relevantes[chunk_id] += 1.0

        # Calcular scores de similaridade
        scores = {}
        for chunk_id, frequencia in chunks_relevantes.items():
            chunk = self.chunks[chunk_id]
            # Score baseado em frequência de palavras-chave
            score = frequencia / len(palavras_query) if palavras_query else 0.0
            scores[chunk_id] = score

        # Ordenar por score
        chunks_ordenados = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limite]

        # Filtrar por tipo se especificado
        chunks_filtrados = []
        scores_filtrados = []

        for chunk_id, score in chunks_ordenados:
            if score < self.LIMITE_SIMILARIDADE:
                continue

            chunk = self.chunks[chunk_id]
            documento = self.documentos[chunk.documento_id]

            if tipo_documento and documento.tipo != tipo_documento:
                continue

            chunks_filtrados.append(chunk)
            scores_filtrados.append(score)

        # Coletar documentos relacionados
        docs_relacionados = []
        for chunk in chunks_filtrados:
            doc = self.documentos[chunk.documento_id]
            if doc not in docs_relacionados:
                docs_relacionados.append(doc)

        tempo_decorrido = (time.time() - tempo_inicio) * 1000

        resultado = ResultadoBusca(
            chunks=chunks_filtrados,
            scores_similaridade=scores_filtrados,
            documentos_relacionados=docs_relacionados,
            tempo_busca_ms=tempo_decorrido,
            total_resultados=len(chunks_filtrados),
        )

        self.historico_busca.append(resultado)
        return resultado

    def _extrair_palavras_chave(self, texto: str) -> List[str]:
        """
        Extrai palavras-chave de um texto.

        Args:
            texto: Texto para extrair palavras-chave

        Returns:
            Lista de palavras-chave
        """
        # Palavras-chave comuns a ignorar
        stop_words = {
            "o", "a", "os", "as", "um", "uma", "uns", "umas",
            "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
            "por", "para", "com", "sem", "e", "ou", "mas", "que", "qual",
            "é", "são", "foi", "foram", "ser", "está", "estão", "tem", "têm",
        }

        # Normalizar e dividir
        palavras = texto.lower().split()

        # Filtrar stop words e palavras muito curtas
        palavras_chave = [
            p.strip(".,;:!?\"'()[]{}") for p in palavras
            if len(p) > 3 and p.lower() not in stop_words
        ]

        return list(set(palavras_chave))

    def _gerar_id_documento(self, titulo: str, fonte: str) -> str:
        """Gera ID único para documento."""
        chave = f"{titulo}_{fonte}".lower().replace(" ", "_")
        return hashlib.md5(chave.encode()).hexdigest()[:16]

    def _calcular_hash(self, conteudo: str) -> str:
        """Calcula hash SHA256 do conteúdo."""
        return hashlib.sha256(conteudo.encode()).hexdigest()

    def obter_documento(self, doc_id: str) -> Optional[Documento]:
        """Obtém documento por ID."""
        return self.documentos.get(doc_id)

    def listar_documentos(
        self,
        tipo: Optional[TipoDocumento] = None,
    ) -> List[Documento]:
        """Lista documentos com filtro opcional."""
        docs = list(self.documentos.values())
        if tipo:
            docs = [d for d in docs if d.tipo == tipo]
        return sorted(docs, key=lambda d: d.data_atualizacao, reverse=True)

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas do RAG."""
        return {
            "total_documentos": len(self.documentos),
            "total_chunks": len(self.chunks),
            "total_palavras_chave": len(self.indice_busca),
            "documentos_por_tipo": {
                tipo.value: len([d for d in self.documentos.values() if d.tipo == tipo])
                for tipo in TipoDocumento
            },
            "buscas_realizadas": len(self.historico_busca),
            "ingestions_realizadas": len(self.historico_ingestion),
        }

    def gerar_relatorio_rag(self) -> Dict[str, Any]:
        """Gera relatório do RAG."""
        stats = self.obter_estatisticas()
        return {
            "status": "operacional",
            "estatisticas": stats,
            "documentos_recentes": [
                {
                    "id": d.id,
                    "titulo": d.titulo,
                    "tipo": d.tipo.value,
                    "data_atualizacao": d.data_atualizacao.isoformat(),
                }
                for d in self.listar_documentos()[:5]
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }


# Instância global do gerenciador
gerenciador_rag = GerenciadorRAG()
