"""
Módulo de Classificação de Risco
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Este módulo implementa regras determinísticas para classificação e análise
de risco. Todas as classificações são auditáveis e rastreáveis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime


class NivelRisco(str, Enum):
    """Níveis de risco."""
    CRITICO = "crítico"
    ALTO = "alto"
    MEDIO = "médio"
    BAIXO = "baixo"
    MINIMO = "mínimo"


class TipoRisco(str, Enum):
    """Tipos de risco."""
    OPERACIONAL = "operacional"
    FINANCEIRO = "financeiro"
    LEGAL = "legal"
    REPUTACIONAL = "reputacional"
    TECNICO = "técnico"
    SEGURANCA = "segurança"
    CONFORMIDADE = "conformidade"


@dataclass
class FatorRisco:
    """Fator individual de risco."""
    nome: str
    tipo: TipoRisco
    probabilidade: float  # 0-1
    impacto: float  # 0-1
    mitigacoes: List[str] = field(default_factory=list)
    evidencias: List[str] = field(default_factory=list)


@dataclass
class ResultadoAnaliseRisco:
    """Resultado completo de análise de risco."""
    risco_geral: float  # 0-1
    nivel_geral: NivelRisco
    fatores_risco: List[FatorRisco]
    risco_por_tipo: Dict[TipoRisco, float]
    matriz_risco: Dict[str, Any]  # Matriz probabilidade x impacto
    fatores_criticos: List[str]
    recomendacoes: List[str]
    plano_mitigacao: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ClassificadorRisco:
    """
    Classificador de risco determinístico.
    Implementa análise quantitativa e qualitativa de risco.
    """

    # Limites de nível de risco
    LIMITE_CRITICO = 0.85
    LIMITE_ALTO = 0.65
    LIMITE_MEDIO = 0.40
    LIMITE_BAIXO = 0.20

    # Pesos por tipo de risco
    PESOS_TIPO_RISCO = {
        TipoRisco.CONFORMIDADE: 0.25,
        TipoRisco.SEGURANCA: 0.25,
        TipoRisco.OPERACIONAL: 0.20,
        TipoRisco.LEGAL: 0.15,
        TipoRisco.FINANCEIRO: 0.10,
        TipoRisco.REPUTACIONAL: 0.03,
        TipoRisco.TECNICO: 0.02,
    }

    def __init__(self):
        """Inicializa o classificador."""
        self.historico_analises: List[ResultadoAnaliseRisco] = []
        self.matriz_risco_cache: Dict[str, Any] = {}

    def analisar_risco(
        self,
        fatores_risco: List[FatorRisco],
        contexto_adicional: Optional[Dict[str, Any]] = None,
    ) -> ResultadoAnaliseRisco:
        """
        Analisa risco baseado em fatores.

        Args:
            fatores_risco: Lista de fatores de risco
            contexto_adicional: Contexto adicional para análise

        Returns:
            ResultadoAnaliseRisco com classificação completa
        """
        if not fatores_risco:
            raise ValueError("Deve haver pelo menos um fator de risco")

        # Calcular risco por tipo
        risco_por_tipo = self._calcular_risco_por_tipo(fatores_risco)

        # Calcular risco geral (ponderado)
        risco_geral = self._calcular_risco_geral(risco_por_tipo)

        # Classificar nível
        nivel_geral = self._classificar_nivel(risco_geral)

        # Construir matriz de risco
        matriz_risco = self._construir_matriz_risco(fatores_risco)

        # Identificar fatores críticos
        fatores_criticos = self._identificar_fatores_criticos(fatores_risco)

        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes(
            fatores_risco, nivel_geral, contexto_adicional
        )

        # Gerar plano de mitigação
        plano_mitigacao = self._gerar_plano_mitigacao(
            fatores_criticos, recomendacoes
        )

        resultado = ResultadoAnaliseRisco(
            risco_geral=risco_geral,
            nivel_geral=nivel_geral,
            fatores_risco=fatores_risco,
            risco_por_tipo=risco_por_tipo,
            matriz_risco=matriz_risco,
            fatores_criticos=fatores_criticos,
            recomendacoes=recomendacoes,
            plano_mitigacao=plano_mitigacao,
        )

        self.historico_analises.append(resultado)
        return resultado

    def _calcular_risco_por_tipo(
        self, fatores_risco: List[FatorRisco]
    ) -> Dict[TipoRisco, float]:
        """
        Calcula risco por tipo.

        Args:
            fatores_risco: Lista de fatores

        Returns:
            Dicionário com risco por tipo
        """
        risco_por_tipo: Dict[TipoRisco, List[float]] = {
            tipo: [] for tipo in TipoRisco
        }

        # Agrupar fatores por tipo
        for fator in fatores_risco:
            risco_fator = fator.probabilidade * fator.impacto
            risco_por_tipo[fator.tipo].append(risco_fator)

        # Calcular média por tipo
        resultado: Dict[TipoRisco, float] = {}
        for tipo, riscos in risco_por_tipo.items():
            if riscos:
                resultado[tipo] = sum(riscos) / len(riscos)
            else:
                resultado[tipo] = 0.0

        return resultado

    def _calcular_risco_geral(
        self, risco_por_tipo: Dict[TipoRisco, float]
    ) -> float:
        """
        Calcula risco geral ponderado.

        Args:
            risco_por_tipo: Risco por tipo

        Returns:
            Risco geral (0-1)
        """
        risco_total = 0.0
        peso_total = 0.0

        for tipo, risco in risco_por_tipo.items():
            peso = self.PESOS_TIPO_RISCO.get(tipo, 0.0)
            risco_total += risco * peso
            peso_total += peso

        if peso_total > 0:
            return min(risco_total / peso_total, 1.0)
        return 0.0

    def _classificar_nivel(self, risco: float) -> NivelRisco:
        """
        Classifica nível de risco.

        Args:
            risco: Valor de risco (0-1)

        Returns:
            NivelRisco classificado
        """
        if risco >= self.LIMITE_CRITICO:
            return NivelRisco.CRITICO
        elif risco >= self.LIMITE_ALTO:
            return NivelRisco.ALTO
        elif risco >= self.LIMITE_MEDIO:
            return NivelRisco.MEDIO
        elif risco >= self.LIMITE_BAIXO:
            return NivelRisco.BAIXO
        else:
            return NivelRisco.MINIMO

    def _construir_matriz_risco(
        self, fatores_risco: List[FatorRisco]
    ) -> Dict[str, Any]:
        """
        Constrói matriz de risco (probabilidade x impacto).

        Args:
            fatores_risco: Lista de fatores

        Returns:
            Matriz de risco estruturada
        """
        # Categorizar fatores em matriz 5x5
        matriz = {
            "celulas": {},
            "distribuicao": {
                "critico": 0,
                "alto": 0,
                "medio": 0,
                "baixo": 0,
                "minimo": 0,
            },
        }

        for fator in fatores_risco:
            # Quantizar probabilidade e impacto em 5 níveis
            prob_nivel = min(int(fator.probabilidade * 5), 4)
            impacto_nivel = min(int(fator.impacto * 5), 4)

            chave = f"{prob_nivel}_{impacto_nivel}"
            if chave not in matriz["celulas"]:
                matriz["celulas"][chave] = []

            matriz["celulas"][chave].append(fator.nome)

            # Classificar célula
            risco_celula = fator.probabilidade * fator.impacto
            nivel_celula = self._classificar_nivel(risco_celula)
            matriz["distribuicao"][nivel_celula.value] += 1

        return matriz

    def _identificar_fatores_criticos(
        self, fatores_risco: List[FatorRisco]
    ) -> List[str]:
        """
        Identifica fatores críticos.

        Args:
            fatores_risco: Lista de fatores

        Returns:
            Lista de fatores críticos
        """
        criticos = []

        for fator in fatores_risco:
            risco_fator = fator.probabilidade * fator.impacto
            if risco_fator >= self.LIMITE_ALTO:
                criticos.append(fator.nome)

        return sorted(criticos)

    def _gerar_recomendacoes(
        self,
        fatores_risco: List[FatorRisco],
        nivel_geral: NivelRisco,
        contexto_adicional: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Gera recomendações baseadas em análise.

        Args:
            fatores_risco: Lista de fatores
            nivel_geral: Nível geral de risco
            contexto_adicional: Contexto adicional

        Returns:
            Lista de recomendações
        """
        recomendacoes = []

        # Recomendações por nível
        if nivel_geral == NivelRisco.CRITICO:
            recomendacoes.append("AÇÃO IMEDIATA NECESSÁRIA: Implementar plano de contingência urgente")
            recomendacoes.append("Escalar para gestão executiva")
            recomendacoes.append("Ativar comitê de crise")

        elif nivel_geral == NivelRisco.ALTO:
            recomendacoes.append("Implementar plano de mitigação em 30 dias")
            recomendacoes.append("Aumentar frequência de monitoramento")
            recomendacoes.append("Designar responsável por mitigação")

        elif nivel_geral == NivelRisco.MEDIO:
            recomendacoes.append("Monitorar regularmente")
            recomendacoes.append("Implementar controles preventivos")
            recomendacoes.append("Revisar anualmente")

        else:
            recomendacoes.append("Manter monitoramento padrão")

        # Recomendações específicas por fator
        for fator in fatores_risco:
            if fator.probabilidade > 0.7:
                recomendacoes.append(
                    f"Reduzir probabilidade de: {fator.nome}"
                )
            if fator.impacto > 0.7:
                recomendacoes.append(
                    f"Reduzir impacto de: {fator.nome}"
                )

        return recomendacoes

    def _gerar_plano_mitigacao(
        self,
        fatores_criticos: List[str],
        recomendacoes: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Gera plano de mitigação.

        Args:
            fatores_criticos: Fatores críticos
            recomendacoes: Recomendações

        Returns:
            Plano de mitigação estruturado
        """
        plano = []

        for i, fator in enumerate(fatores_criticos, 1):
            acao = {
                "id": f"acao_{i}",
                "fator": fator,
                "prioridade": "alta" if i <= 3 else "média",
                "prazo": "30 dias" if i <= 3 else "60 dias",
                "responsavel": "A designar",
                "status": "pendente",
                "metricas": [
                    "Redução de probabilidade",
                    "Redução de impacto",
                ],
            }
            plano.append(acao)

        return plano

    def obter_historico_analises(self) -> List[ResultadoAnaliseRisco]:
        """Retorna histórico de análises."""
        return self.historico_analises.copy()

    def gerar_relatorio_risco(
        self, resultado: ResultadoAnaliseRisco
    ) -> Dict[str, Any]:
        """
        Gera relatório de risco.

        Args:
            resultado: Resultado da análise

        Returns:
            Dicionário com relatório estruturado
        """
        return {
            "risco_geral": round(resultado.risco_geral, 3),
            "nivel_geral": resultado.nivel_geral.value,
            "risco_por_tipo": {
                tipo.value: round(risco, 3)
                for tipo, risco in resultado.risco_por_tipo.items()
            },
            "total_fatores": len(resultado.fatores_risco),
            "fatores_criticos": resultado.fatores_criticos,
            "total_recomendacoes": len(resultado.recomendacoes),
            "plano_mitigacao_itens": len(resultado.plano_mitigacao),
            "timestamp": resultado.timestamp.isoformat(),
        }


# Instância global do classificador
classificador = ClassificadorRisco()
