"""
Módulo de Cálculos e Coeficientes Determinísticos
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Este módulo implementa cálculos técnicos e coeficientes utilizados
na análise normativa e conformidade. Todos os cálculos são determinísticos
e auditáveis.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class RiskLevel(str, Enum):
    """Classificação de nível de risco."""
    BAIXO = "baixo"
    MEDIO = "médio"
    ALTO = "alto"


@dataclass
class IndiceConformidade:
    """Resultado do cálculo de índice de conformidade."""
    valor: float  # 0-100
    percentual: float  # 0-100
    status: str  # "conforme", "parcial", "não_conforme"
    detalhes: Dict[str, float]
    timestamp: datetime


@dataclass
class CoeficienteRisco:
    """Resultado do cálculo de coeficiente de risco."""
    valor: float  # 0-1
    nivel: RiskLevel
    fatores: Dict[str, float]
    recomendacoes: List[str]
    timestamp: datetime


class CalculadoraIndices:
    """
    Calculadora de índices técnicos e coeficientes.
    Implementa lógica determinística para análise de conformidade.
    """

    # Constantes de ponderação
    PESO_CONFORMIDADE_LEGAL = 0.35
    PESO_CONFORMIDADE_TECNICA = 0.40
    PESO_CONFORMIDADE_OPERACIONAL = 0.25

    # Limites de conformidade
    LIMITE_CONFORME = 95.0
    LIMITE_PARCIAL = 70.0

    # Limites de risco
    LIMITE_RISCO_ALTO = 0.7
    LIMITE_RISCO_MEDIO = 0.4

    def __init__(self):
        """Inicializa a calculadora."""
        self.historico: List[IndiceConformidade] = []
        self.historico_risco: List[CoeficienteRisco] = []

    def calcular_conformidade(
        self,
        conformidade_legal: float,
        conformidade_tecnica: float,
        conformidade_operacional: float,
        detalhes_adicionais: Optional[Dict[str, float]] = None,
    ) -> IndiceConformidade:
        """
        Calcula índice de conformidade ponderado.

        Args:
            conformidade_legal: Índice de conformidade legal (0-100)
            conformidade_tecnica: Índice de conformidade técnica (0-100)
            conformidade_operacional: Índice de conformidade operacional (0-100)
            detalhes_adicionais: Detalhes adicionais para auditoria

        Returns:
            IndiceConformidade com resultado ponderado
        """
        # Validar entradas
        for valor in [conformidade_legal, conformidade_tecnica, conformidade_operacional]:
            if not 0 <= valor <= 100:
                raise ValueError(f"Conformidade deve estar entre 0 e 100, recebido: {valor}")

        # Calcular ponderação
        valor_ponderado = (
            conformidade_legal * self.PESO_CONFORMIDADE_LEGAL
            + conformidade_tecnica * self.PESO_CONFORMIDADE_TECNICA
            + conformidade_operacional * self.PESO_CONFORMIDADE_OPERACIONAL
        )

        # Determinar status
        if valor_ponderado >= self.LIMITE_CONFORME:
            status = "conforme"
        elif valor_ponderado >= self.LIMITE_PARCIAL:
            status = "parcial"
        else:
            status = "não_conforme"

        # Montar detalhes
        detalhes = {
            "legal": conformidade_legal,
            "tecnica": conformidade_tecnica,
            "operacional": conformidade_operacional,
            "ponderado": valor_ponderado,
        }
        if detalhes_adicionais:
            detalhes.update(detalhes_adicionais)

        resultado = IndiceConformidade(
            valor=valor_ponderado,
            percentual=valor_ponderado,
            status=status,
            detalhes=detalhes,
            timestamp=datetime.utcnow(),
        )

        self.historico.append(resultado)
        return resultado

    def calcular_risco(
        self,
        fatores_risco: Dict[str, float],
        pesos: Optional[Dict[str, float]] = None,
    ) -> CoeficienteRisco:
        """
        Calcula coeficiente de risco baseado em fatores.

        Args:
            fatores_risco: Dicionário com fatores de risco (0-1)
            pesos: Pesos para cada fator (opcional, usa iguais se não fornecido)

        Returns:
            CoeficienteRisco com classificação e recomendações
        """
        # Validar entradas
        for fator, valor in fatores_risco.items():
            if not 0 <= valor <= 1:
                raise ValueError(f"Fator {fator} deve estar entre 0 e 1, recebido: {valor}")

        # Usar pesos iguais se não fornecido
        if pesos is None:
            pesos = {fator: 1.0 / len(fatores_risco) for fator in fatores_risco}

        # Validar pesos
        if abs(sum(pesos.values()) - 1.0) > 0.01:
            raise ValueError("Soma dos pesos deve ser 1.0")

        # Calcular risco ponderado
        valor_risco = sum(
            fatores_risco.get(fator, 0) * peso
            for fator, peso in pesos.items()
        )

        # Classificar nível
        if valor_risco >= self.LIMITE_RISCO_ALTO:
            nivel = RiskLevel.ALTO
        elif valor_risco >= self.LIMITE_RISCO_MEDIO:
            nivel = RiskLevel.MEDIO
        else:
            nivel = RiskLevel.BAIXO

        # Gerar recomendações
        recomendacoes = self._gerar_recomendacoes_risco(
            fatores_risco, valor_risco, nivel
        )

        resultado = CoeficienteRisco(
            valor=valor_risco,
            nivel=nivel,
            fatores=fatores_risco,
            recomendacoes=recomendacoes,
            timestamp=datetime.utcnow(),
        )

        self.historico_risco.append(resultado)
        return resultado

    def _gerar_recomendacoes_risco(
        self,
        fatores_risco: Dict[str, float],
        valor_risco: float,
        nivel: RiskLevel,
    ) -> List[str]:
        """
        Gera recomendações baseadas em fatores de risco.

        Args:
            fatores_risco: Dicionário de fatores
            valor_risco: Valor total de risco
            nivel: Nível de risco classificado

        Returns:
            Lista de recomendações
        """
        recomendacoes = []

        if nivel == RiskLevel.ALTO:
            recomendacoes.append("Ação imediata necessária para mitigação de risco")
            recomendacoes.append("Implementar plano de contingência")
            recomendacoes.append("Aumentar frequência de monitoramento")

        elif nivel == RiskLevel.MEDIO:
            recomendacoes.append("Monitorar fatores críticos regularmente")
            recomendacoes.append("Implementar controles preventivos")

        else:
            recomendacoes.append("Manter monitoramento padrão")

        # Adicionar recomendações específicas por fator
        for fator, valor in fatores_risco.items():
            if valor > 0.7:
                recomendacoes.append(f"Revisar fator crítico: {fator}")

        return recomendacoes

    def calcular_neuro_index_l10(
        self,
        clareza: float,
        consistencia: float,
        completude: float,
    ) -> float:
        """
        Calcula NeuroIndex L10 (índice de qualidade de análise).

        Args:
            clareza: Índice de clareza (0-10)
            consistencia: Índice de consistência (0-10)
            completude: Índice de completude (0-10)

        Returns:
            NeuroIndex L10 (0-10)
        """
        # Validar entradas
        for valor in [clareza, consistencia, completude]:
            if not 0 <= valor <= 10:
                raise ValueError(f"Índice deve estar entre 0 e 10, recebido: {valor}")

        # Calcular média ponderada
        neuro_index = (
            clareza * 0.4 +
            consistencia * 0.35 +
            completude * 0.25
        )

        return round(neuro_index, 2)

    def calcular_confiabilidade(
        self,
        precisao_dados: float,
        cobertura_analise: float,
        validacao_cruzada: float,
    ) -> float:
        """
        Calcula índice de confiabilidade da análise.

        Args:
            precisao_dados: Precisão dos dados (0-1)
            cobertura_analise: Cobertura da análise (0-1)
            validacao_cruzada: Resultado de validação cruzada (0-1)

        Returns:
            Índice de confiabilidade (0-1)
        """
        # Validar entradas
        for valor in [precisao_dados, cobertura_analise, validacao_cruzada]:
            if not 0 <= valor <= 1:
                raise ValueError(f"Valor deve estar entre 0 e 1, recebido: {valor}")

        # Calcular confiabilidade
        confiabilidade = (
            precisao_dados * 0.45 +
            cobertura_analise * 0.35 +
            validacao_cruzada * 0.20
        )

        return round(confiabilidade, 3)

    def obter_historico_conformidade(self) -> List[IndiceConformidade]:
        """Retorna histórico de cálculos de conformidade."""
        return self.historico.copy()

    def obter_historico_risco(self) -> List[CoeficienteRisco]:
        """Retorna histórico de cálculos de risco."""
        return self.historico_risco.copy()

    def limpar_historico(self) -> None:
        """Limpa histórico de cálculos."""
        self.historico.clear()
        self.historico_risco.clear()


# Instância global da calculadora
calculadora = CalculadoraIndices()
