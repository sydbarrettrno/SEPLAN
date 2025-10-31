"""
Modelos de Dados da API
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class TipoAnalise(str, Enum):
    """Tipos de análise suportados."""
    FAQ = "faq"
    CALCULO = "calculo"
    AUDITORIA = "auditoria"
    CONFORMIDADE = "conformidade"
    RISCO = "risco"
    PARECER = "parecer"


class NivelRisco(str, Enum):
    """Níveis de risco."""
    CRITICO = "crítico"
    ALTO = "alto"
    MEDIO = "médio"
    BAIXO = "baixo"
    MINIMO = "mínimo"


class StatusValidacao(str, Enum):
    """Status de validação."""
    CONFORME = "conforme"
    NAO_CONFORME = "não_conforme"
    PARCIAL = "parcial"
    PENDENTE = "pendente"


# ============================================================================
# Modelos de Requisição
# ============================================================================

class AnaliseRequest(BaseModel):
    """Requisição de análise."""
    titulo: str = Field(..., description="Título da análise")
    tipo_analise: TipoAnalise = Field(..., description="Tipo de análise")
    conteudo: str = Field(..., description="Conteúdo a analisar")
    contexto: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    normas_aplicaveis: Optional[List[str]] = Field(None, description="Normas aplicáveis")
    tags: Optional[List[str]] = Field(None, description="Tags para classificação")

    class Config:
        json_schema_extra = {
            "example": {
                "titulo": "Análise de Conformidade",
                "tipo_analise": "conformidade",
                "conteudo": "Documento técnico a analisar...",
                "normas_aplicaveis": ["ABNT_NBR_ISO_9001"],
                "tags": ["qualidade", "processo"],
            }
        }


class DocumentoRAGRequest(BaseModel):
    """Requisição para ingestion de documento no RAG."""
    titulo: str = Field(..., description="Título do documento")
    conteudo: str = Field(..., description="Conteúdo do documento")
    tipo: str = Field(..., description="Tipo de documento")
    fonte: str = Field(..., description="Fonte/origem do documento")
    tags: Optional[List[str]] = Field(None, description="Tags")
    metadados: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class BuscaRAGRequest(BaseModel):
    """Requisição de busca no RAG."""
    query: str = Field(..., description="Consulta de busca")
    tipo_documento: Optional[str] = Field(None, description="Filtrar por tipo")
    limite: Optional[int] = Field(5, description="Limite de resultados")


# ============================================================================
# Modelos de Resposta
# ============================================================================

class MetricasAnalise(BaseModel):
    """Métricas de uma análise."""
    conformidade: float = Field(..., description="Índice de conformidade (0-100)")
    confiabilidade: float = Field(..., description="Índice de confiabilidade (0-1)")
    tempo_processamento_ms: float = Field(..., description="Tempo de processamento em ms")
    clareza: float = Field(..., description="Índice de clareza (0-10)")
    cobertura: float = Field(..., description="Cobertura da análise (0-1)")
    neuro_index_l10: float = Field(..., description="NeuroIndex L10 (0-10)")


class AchadoAnalise(BaseModel):
    """Achado de uma análise."""
    id: str
    titulo: str
    descricao: str
    severidade: str  # crítica, alta, média, baixa
    norma_ref: Optional[str] = None
    status: str
    recomendacao: Optional[str] = None


class AnaliseResponse(BaseModel):
    """Resposta de análise."""
    id: str = Field(..., description="ID da análise")
    titulo: str
    tipo_analise: TipoAnalise
    status: str = Field(..., description="Status da análise")
    contexto_enquadramento: str = Field(..., description="Contexto e enquadramento")
    fundamentacao_tecnica: str = Field(..., description="Fundamentação técnica/legal")
    analise_dados: str = Field(..., description="Análise de dados")
    achados: List[AchadoAnalise] = Field(..., description="Achados identificados")
    risco_geral: NivelRisco = Field(..., description="Nível de risco geral")
    recomendacoes: List[str] = Field(..., description="Recomendações")
    sintese_final: str = Field(..., description="Síntese final")
    metricas: MetricasAnalise
    credito_autoral: str = Field(default="Criado por Eng. Anibal Nisgoski")
    timestamp: datetime
    url_relatorio: Optional[str] = Field(None, description="URL do relatório gerado")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "analise_001",
                "titulo": "Análise de Conformidade",
                "tipo_analise": "conformidade",
                "status": "concluída",
                "contexto_enquadramento": "Análise de conformidade com ABNT NBR ISO 9001...",
                "fundamentacao_tecnica": "A norma ABNT NBR ISO 9001 estabelece...",
                "analise_dados": "Os dados fornecidos indicam...",
                "achados": [],
                "risco_geral": "médio",
                "recomendacoes": ["Implementar controle de documentação"],
                "sintese_final": "A análise conclui que...",
                "metricas": {
                    "conformidade": 85.5,
                    "confiabilidade": 0.92,
                    "tempo_processamento_ms": 2500,
                    "clareza": 8.5,
                    "cobertura": 1.0,
                    "neuro_index_l10": 8.3,
                },
                "credito_autoral": "Criado por Eng. Anibal Nisgoski",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class DocumentoRAGResponse(BaseModel):
    """Resposta de documento no RAG."""
    id: str
    titulo: str
    tipo: str
    fonte: str
    data_criacao: datetime
    data_atualizacao: datetime
    tags: List[str]
    total_chunks: int


class ChunkRAGResponse(BaseModel):
    """Resposta de chunk do RAG."""
    id: str
    documento_id: str
    conteudo: str
    numero_sequencia: int
    score_similaridade: Optional[float] = None


class BuscaRAGResponse(BaseModel):
    """Resposta de busca no RAG."""
    chunks: List[ChunkRAGResponse]
    documentos_relacionados: List[DocumentoRAGResponse]
    tempo_busca_ms: float
    total_resultados: int


class EstatisticasRAGResponse(BaseModel):
    """Resposta com estatísticas do RAG."""
    total_documentos: int
    total_chunks: int
    total_palavras_chave: int
    documentos_por_tipo: Dict[str, int]
    buscas_realizadas: int
    ingestions_realizadas: int


class HealthCheckResponse(BaseModel):
    """Resposta de health check."""
    status: str = Field(..., description="Status da aplicação")
    versao: str = Field(..., description="Versão da aplicação")
    autor: str = Field(..., description="Autor da aplicação")
    timestamp: datetime
    componentes: Dict[str, str] = Field(..., description="Status dos componentes")


class ErrorResponse(BaseModel):
    """Resposta de erro."""
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    timestamp: datetime
    request_id: Optional[str] = Field(None, description="ID da requisição")


# ============================================================================
# Modelos Internos
# ============================================================================

class AnaliseInterna(BaseModel):
    """Modelo interno de análise para processamento."""
    id: str
    titulo: str
    tipo_analise: TipoAnalise
    conteudo: str
    contexto: Dict[str, Any]
    normas_aplicaveis: List[str]
    tags: List[str]
    timestamp_criacao: datetime
    timestamp_conclusao: Optional[datetime] = None
    status: str = "processando"
    resultado: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None
