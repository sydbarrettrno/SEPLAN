"""
Endpoint Principal de Análise
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa o fluxo completo de análise:
1. Classificar intenção
2. Validar dados mínimos
3. Executar funções determinísticas
4. Buscar contexto no RAG
5. Compor parecer e gerar relatório
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import asyncio

from api.models import (
    AnaliseRequest,
    AnaliseResponse,
    TipoAnalise,
    MetricasAnalise,
    AchadoAnalise,
    NivelRisco,
)
from api.calc.indices import calculadora, RiskLevel
from api.rules.conformidade import validador, StatusValidacao
from api.rules.risco import classificador, FatorRisco, TipoRisco
from api.rag.manager import gerenciador_rag, TipoDocumento


class ProcessadorAnalise:
    """Processador de análises do sistema."""

    def __init__(self):
        """Inicializa o processador."""
        self.historico_analises: Dict[str, Dict[str, Any]] = {}

    async def processar_analise(
        self, requisicao: AnaliseRequest
    ) -> AnaliseResponse:
        """
        Processa uma análise completa.

        Args:
            requisicao: Requisição de análise

        Returns:
            AnaliseResponse com resultado completo
        """
        # Gerar ID único
        analise_id = str(uuid.uuid4())[:8]
        timestamp_inicio = datetime.utcnow()

        try:
            # 1. Classificar intenção
            tipo_classificado = self._classificar_intencao(
                requisicao.tipo_analise, requisicao.conteudo
            )

            # 2. Validar dados mínimos
            self._validar_dados_minimos(requisicao)

            # 3. Executar funções determinísticas
            resultado_conformidade = await self._executar_conformidade(
                requisicao, tipo_classificado
            )

            resultado_risco = await self._executar_risco(
                requisicao, tipo_classificado
            )

            # 4. Buscar contexto no RAG
            contexto_rag = await self._buscar_contexto_rag(requisicao)

            # 5. Compor parecer
            parecer = await self._compor_parecer(
                requisicao,
                resultado_conformidade,
                resultado_risco,
                contexto_rag,
            )

            # Calcular métricas
            metricas = self._calcular_metricas(
                resultado_conformidade,
                resultado_risco,
                timestamp_inicio,
            )

            # Construir resposta
            resposta = AnaliseResponse(
                id=analise_id,
                titulo=requisicao.titulo,
                tipo_analise=tipo_classificado,
                status="concluída",
                contexto_enquadramento=parecer["contexto_enquadramento"],
                fundamentacao_tecnica=parecer["fundamentacao_tecnica"],
                analise_dados=parecer["analise_dados"],
                achados=self._converter_achados(resultado_conformidade.get("achados", [])),
                risco_geral=NivelRisco(resultado_risco["nivel_geral"]),
                recomendacoes=parecer["recomendacoes"],
                sintese_final=parecer["sintese_final"],
                metricas=metricas,
                timestamp=datetime.utcnow(),
            )

            # Armazenar no histórico
            self.historico_analises[analise_id] = {
                "requisicao": requisicao.dict(),
                "resposta": resposta.dict(),
                "timestamp": timestamp_inicio.isoformat(),
            }

            return resposta

        except Exception as e:
            # Retornar erro
            raise Exception(f"Erro ao processar análise: {str(e)}")

    def _classificar_intencao(
        self, tipo_solicitado: TipoAnalise, conteudo: str
    ) -> TipoAnalise:
        """
        Classifica a intenção da análise.

        Args:
            tipo_solicitado: Tipo solicitado
            conteudo: Conteúdo a analisar

        Returns:
            Tipo de análise classificado
        """
        # Palavras-chave por tipo
        palavras_chave = {
            TipoAnalise.FAQ: ["qual", "como", "por que", "o que", "quando"],
            TipoAnalise.CALCULO: ["calcular", "valor", "índice", "coeficiente", "resultado"],
            TipoAnalise.AUDITORIA: ["auditoria", "verificar", "inspecionar", "revisar"],
            TipoAnalise.CONFORMIDADE: ["conforme", "norma", "regulamento", "requisito"],
            TipoAnalise.RISCO: ["risco", "perigo", "ameaça", "vulnerabilidade"],
            TipoAnalise.PARECER: ["parecer", "opinião", "análise", "conclusão"],
        }

        conteudo_lower = conteudo.lower()
        pontuacoes = {}

        for tipo, palavras in palavras_chave.items():
            pontuacoes[tipo] = sum(
                1 for palavra in palavras if palavra in conteudo_lower
            )

        # Retornar tipo com maior pontuação ou o solicitado
        tipo_detectado = max(pontuacoes, key=pontuacoes.get)

        if pontuacoes[tipo_detectado] > 0:
            return tipo_detectado
        return tipo_solicitado

    def _validar_dados_minimos(self, requisicao: AnaliseRequest) -> None:
        """
        Valida dados mínimos.

        Args:
            requisicao: Requisição a validar

        Raises:
            ValueError: Se dados mínimos não forem atendidos
        """
        if not requisicao.titulo or len(requisicao.titulo.strip()) < 3:
            raise ValueError("Título deve ter pelo menos 3 caracteres")

        if not requisicao.conteudo or len(requisicao.conteudo.strip()) < 10:
            raise ValueError("Conteúdo deve ter pelo menos 10 caracteres")

        if not requisicao.tipo_analise:
            raise ValueError("Tipo de análise é obrigatório")

    async def _executar_conformidade(
        self, requisicao: AnaliseRequest, tipo: TipoAnalise
    ) -> Dict[str, Any]:
        """
        Executa análise de conformidade.

        Args:
            requisicao: Requisição
            tipo: Tipo de análise

        Returns:
            Resultado de conformidade
        """
        # Dados simulados para análise
        dados_analise = {
            "documentacao": True,
            "responsabilidades": True,
            "controles": True,
            "politica": True,
            "seguranca": True,
            "risco": True,
        }

        # Validar conformidade
        normas = requisicao.normas_aplicaveis or [
            "ABNT_NBR_ISO_9001",
            "ABNT_NBR_ISO_27001",
        ]

        resultado_validacao = validador.validar_conformidade(
            dados_analise, normas
        )

        # Converter para dicionário
        return {
            "conformidade_geral": resultado_validacao.conformidade_geral,
            "status_geral": resultado_validacao.status_geral.value,
            "achados": [
                {
                    "id": a.id,
                    "titulo": a.titulo,
                    "descricao": a.descricao,
                    "severidade": a.severidade,
                    "norma_ref": a.norma_ref,
                    "status": a.status.value,
                    "recomendacao": a.recomendacao,
                }
                for a in resultado_validacao.achados
            ],
            "conformidade_por_norma": resultado_validacao.conformidade_por_norma,
        }

    async def _executar_risco(
        self, requisicao: AnaliseRequest, tipo: TipoAnalise
    ) -> Dict[str, Any]:
        """
        Executa análise de risco.

        Args:
            requisicao: Requisição
            tipo: Tipo de análise

        Returns:
            Resultado de risco
        """
        # Fatores de risco simulados
        fatores = [
            FatorRisco(
                nome="Conformidade com normas",
                tipo=TipoRisco.CONFORMIDADE,
                probabilidade=0.3,
                impacto=0.8,
                mitigacoes=["Implementar controles"],
            ),
            FatorRisco(
                nome="Segurança de dados",
                tipo=TipoRisco.SEGURANCA,
                probabilidade=0.4,
                impacto=0.9,
                mitigacoes=["Criptografia", "Backup"],
            ),
            FatorRisco(
                nome="Operações",
                tipo=TipoRisco.OPERACIONAL,
                probabilidade=0.2,
                impacto=0.5,
                mitigacoes=["Procedimentos"],
            ),
        ]

        # Analisar risco
        resultado_risco = classificador.analisar_risco(fatores)

        # Converter para dicionário
        return {
            "risco_geral": round(resultado_risco.risco_geral, 3),
            "nivel_geral": resultado_risco.nivel_geral.value,
            "fatores_criticos": resultado_risco.fatores_criticos,
            "recomendacoes": resultado_risco.recomendacoes,
            "risco_por_tipo": {
                tipo.value: round(risco, 3)
                for tipo, risco in resultado_risco.risco_por_tipo.items()
            },
        }

    async def _buscar_contexto_rag(
        self, requisicao: AnaliseRequest
    ) -> Dict[str, Any]:
        """
        Busca contexto no RAG.

        Args:
            requisicao: Requisição

        Returns:
            Contexto do RAG
        """
        # Buscar documentos relacionados
        resultado_busca = gerenciador_rag.buscar(
            requisicao.conteudo,
            limite=3,
        )

        return {
            "total_documentos": resultado_busca.total_resultados,
            "documentos": [
                {
                    "titulo": doc.titulo,
                    "tipo": doc.tipo.value,
                    "fonte": doc.fonte,
                }
                for doc in resultado_busca.documentos_relacionados
            ],
            "tempo_busca_ms": resultado_busca.tempo_busca_ms,
        }

    async def _compor_parecer(
        self,
        requisicao: AnaliseRequest,
        resultado_conformidade: Dict[str, Any],
        resultado_risco: Dict[str, Any],
        contexto_rag: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Compõe parecer técnico.

        Args:
            requisicao: Requisição
            resultado_conformidade: Resultado de conformidade
            resultado_risco: Resultado de risco
            contexto_rag: Contexto do RAG

        Returns:
            Parecer estruturado
        """
        return {
            "contexto_enquadramento": (
                f"Análise técnico-normativa de: {requisicao.titulo}. "
                f"Tipo: {requisicao.tipo_analise.value}. "
                f"Documentos de referência: {contexto_rag['total_documentos']}."
            ),
            "fundamentacao_tecnica": (
                f"A análise baseia-se em normas ABNT, ISO e regulamentações aplicáveis. "
                f"Conformidade geral: {resultado_conformidade['conformidade_geral']:.1f}%. "
                f"Status: {resultado_conformidade['status_geral']}."
            ),
            "analise_dados": (
                f"Foram analisados dados de conformidade e risco. "
                f"Risco geral identificado: {resultado_risco['nivel_geral']}. "
                f"Fatores críticos: {len(resultado_risco['fatores_criticos'])}."
            ),
            "recomendacoes": resultado_risco["recomendacoes"],
            "sintese_final": (
                f"A análise conclui que o nível de conformidade é "
                f"{resultado_conformidade['status_geral']} com risco "
                f"{resultado_risco['nivel_geral']}. Recomenda-se implementar "
                f"as ações de mitigação propostas conforme prioridade."
            ),
        }

    def _calcular_metricas(
        self,
        resultado_conformidade: Dict[str, Any],
        resultado_risco: Dict[str, Any],
        timestamp_inicio: datetime,
    ) -> MetricasAnalise:
        """
        Calcula métricas da análise.

        Args:
            resultado_conformidade: Resultado de conformidade
            resultado_risco: Resultado de risco
            timestamp_inicio: Timestamp de início

        Returns:
            MetricasAnalise calculadas
        """
        tempo_ms = (datetime.utcnow() - timestamp_inicio).total_seconds() * 1000

        # Calcular NeuroIndex L10
        clareza = 8.5
        consistencia = 8.0
        completude = 8.2
        neuro_index = calculadora.calcular_neuro_index_l10(
            clareza, consistencia, completude
        )

        # Calcular confiabilidade
        precisao = 0.95
        cobertura = 1.0
        validacao_cruzada = 0.90
        confiabilidade = calculadora.calcular_confiabilidade(
            precisao, cobertura, validacao_cruzada
        )

        return MetricasAnalise(
            conformidade=resultado_conformidade["conformidade_geral"],
            confiabilidade=confiabilidade,
            tempo_processamento_ms=tempo_ms,
            clareza=clareza,
            cobertura=cobertura,
            neuro_index_l10=neuro_index,
        )

    def _converter_achados(self, achados_raw: List[Dict]) -> List[AchadoAnalise]:
        """Converte achados brutos para modelo."""
        return [
            AchadoAnalise(
                id=a.get("id", ""),
                titulo=a.get("titulo", ""),
                descricao=a.get("descricao", ""),
                severidade=a.get("severidade", "média"),
                norma_ref=a.get("norma_ref"),
                status=a.get("status", "pendente"),
                recomendacao=a.get("recomendacao"),
            )
            for a in achados_raw
        ]

    def obter_analise(self, analise_id: str) -> Optional[Dict[str, Any]]:
        """Obtém análise do histórico."""
        return self.historico_analises.get(analise_id)

    def listar_analises(self) -> List[Dict[str, Any]]:
        """Lista todas as análises."""
        return list(self.historico_analises.values())


# Instância global
processador = ProcessadorAnalise()
