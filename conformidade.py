"""
Módulo de Regras de Conformidade Técnico-Normativa
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Este módulo implementa regras determinísticas para validação de conformidade
com normas técnicas e regulamentações. Todas as regras são auditáveis e
rastreáveis.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime


class TipoNorma(str, Enum):
    """Tipos de normas técnicas."""
    ABNT = "ABNT"
    ISO = "ISO"
    NBR = "NBR"
    REGULAMENTACAO = "regulamentacao"
    INTERNA = "interna"


class StatusValidacao(str, Enum):
    """Status de validação de conformidade."""
    CONFORME = "conforme"
    NAO_CONFORME = "não_conforme"
    PARCIAL = "parcial"
    PENDENTE = "pendente"


@dataclass
class Achado:
    """Registro de achado de conformidade."""
    id: str
    titulo: str
    descricao: str
    severidade: str  # "crítica", "alta", "média", "baixa"
    norma_ref: str
    status: StatusValidacao
    evidencia: Optional[str] = None
    recomendacao: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResultadoValidacao:
    """Resultado completo de validação de conformidade."""
    conformidade_geral: float  # 0-100
    status_geral: StatusValidacao
    achados: List[Achado]
    normas_aplicaveis: List[str]
    conformidade_por_norma: Dict[str, float]
    inconsistencias: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ValidadorConformidade:
    """
    Validador de conformidade técnico-normativa.
    Implementa regras determinísticas para análise de conformidade.
    """

    def __init__(self):
        """Inicializa o validador."""
        self.regras: Dict[str, Callable] = {}
        self.normas_registradas: Dict[str, Dict[str, Any]] = {}
        self._registrar_normas_padrao()
        self.historico_validacoes: List[ResultadoValidacao] = []

    def _registrar_normas_padrao(self) -> None:
        """Registra normas padrão do sistema."""
        # ABNT NBR ISO 9001 - Gestão de Qualidade
        self.normas_registradas["ABNT_NBR_ISO_9001"] = {
            "tipo": TipoNorma.ABNT,
            "titulo": "Sistemas de gestão da qualidade",
            "requisitos": [
                "Documentação de processos",
                "Responsabilidades definidas",
                "Controle de registros",
                "Avaliação de conformidade",
            ],
            "peso": 0.25,
        }

        # ABNT NBR ISO 27001 - Segurança da Informação
        self.normas_registradas["ABNT_NBR_ISO_27001"] = {
            "tipo": TipoNorma.ABNT,
            "titulo": "Segurança da informação",
            "requisitos": [
                "Política de segurança",
                "Controle de acesso",
                "Criptografia de dados",
                "Plano de continuidade",
            ],
            "peso": 0.30,
        }

        # ABNT NBR 14724 - Apresentação de trabalhos acadêmicos
        self.normas_registradas["ABNT_NBR_14724"] = {
            "tipo": TipoNorma.ABNT,
            "titulo": "Informação e documentação - Trabalhos acadêmicos",
            "requisitos": [
                "Formatação de texto",
                "Estrutura de documento",
                "Referências bibliográficas",
                "Apresentação de tabelas",
            ],
            "peso": 0.15,
        }

        # ISO 31000 - Gestão de Risco
        self.normas_registradas["ISO_31000"] = {
            "tipo": TipoNorma.ISO,
            "titulo": "Gestão de risco",
            "requisitos": [
                "Identificação de riscos",
                "Análise de probabilidade",
                "Avaliação de impacto",
                "Plano de mitigação",
            ],
            "peso": 0.20,
        }

        # Regulamentação Interna
        self.normas_registradas["REGULAMENTACAO_INTERNA"] = {
            "tipo": TipoNorma.REGULAMENTACAO,
            "titulo": "Regulamentação interna da organização",
            "requisitos": [
                "Políticas internas",
                "Procedimentos operacionais",
                "Diretrizes de segurança",
                "Padrões de qualidade",
            ],
            "peso": 0.10,
        }

    def registrar_norma(
        self,
        codigo: str,
        tipo: TipoNorma,
        titulo: str,
        requisitos: List[str],
        peso: float = 0.1,
    ) -> None:
        """
        Registra uma nova norma no validador.

        Args:
            codigo: Código único da norma
            tipo: Tipo de norma
            titulo: Título descritivo
            requisitos: Lista de requisitos
            peso: Peso da norma na análise (0-1)
        """
        if not 0 <= peso <= 1:
            raise ValueError(f"Peso deve estar entre 0 e 1, recebido: {peso}")

        self.normas_registradas[codigo] = {
            "tipo": tipo,
            "titulo": titulo,
            "requisitos": requisitos,
            "peso": peso,
        }

    def validar_conformidade(
        self,
        dados_analise: Dict[str, Any],
        normas_aplicaveis: Optional[List[str]] = None,
    ) -> ResultadoValidacao:
        """
        Valida conformidade dos dados contra normas aplicáveis.

        Args:
            dados_analise: Dados a validar
            normas_aplicaveis: Lista de normas a aplicar (usa todas se None)

        Returns:
            ResultadoValidacao com achados e conformidade
        """
        if normas_aplicaveis is None:
            normas_aplicaveis = list(self.normas_registradas.keys())

        achados: List[Achado] = []
        conformidade_por_norma: Dict[str, float] = {}
        inconsistencias: List[str] = []

        # Validar contra cada norma
        for norma_codigo in normas_aplicaveis:
            if norma_codigo not in self.normas_registradas:
                inconsistencias.append(f"Norma não registrada: {norma_codigo}")
                continue

            norma = self.normas_registradas[norma_codigo]
            conformidade = self._validar_contra_norma(
                dados_analise, norma_codigo, norma, achados
            )
            conformidade_por_norma[norma_codigo] = conformidade

        # Calcular conformidade geral (ponderada)
        conformidade_geral = self._calcular_conformidade_ponderada(
            conformidade_por_norma, normas_aplicaveis
        )

        # Determinar status geral
        if conformidade_geral >= 95:
            status_geral = StatusValidacao.CONFORME
        elif conformidade_geral >= 70:
            status_geral = StatusValidacao.PARCIAL
        else:
            status_geral = StatusValidacao.NAO_CONFORME

        resultado = ResultadoValidacao(
            conformidade_geral=conformidade_geral,
            status_geral=status_geral,
            achados=achados,
            normas_aplicaveis=normas_aplicaveis,
            conformidade_por_norma=conformidade_por_norma,
            inconsistencias=inconsistencias,
        )

        self.historico_validacoes.append(resultado)
        return resultado

    def _validar_contra_norma(
        self,
        dados_analise: Dict[str, Any],
        norma_codigo: str,
        norma: Dict[str, Any],
        achados: List[Achado],
    ) -> float:
        """
        Valida dados contra uma norma específica.

        Args:
            dados_analise: Dados a validar
            norma_codigo: Código da norma
            norma: Definição da norma
            achados: Lista para adicionar achados

        Returns:
            Percentual de conformidade (0-100)
        """
        requisitos = norma.get("requisitos", [])
        conformidades = []

        for i, requisito in enumerate(requisitos):
            # Simular validação de requisito
            # Em produção, isso seria mais complexo
            conforme = self._validar_requisito(
                dados_analise, norma_codigo, requisito
            )

            if not conforme:
                achado = Achado(
                    id=f"{norma_codigo}_req_{i}",
                    titulo=f"Não conformidade: {requisito}",
                    descricao=f"Requisito '{requisito}' da norma {norma_codigo} não foi atendido",
                    severidade="média",
                    norma_ref=norma_codigo,
                    status=StatusValidacao.NAO_CONFORME,
                    recomendacao=f"Implementar controle para: {requisito}",
                )
                achados.append(achado)

            conformidades.append(1.0 if conforme else 0.0)

        # Calcular conformidade média
        if conformidades:
            conformidade_media = sum(conformidades) / len(conformidades) * 100
        else:
            conformidade_media = 100.0

        return conformidade_media

    def _validar_requisito(
        self,
        dados_analise: Dict[str, Any],
        norma_codigo: str,
        requisito: str,
    ) -> bool:
        """
        Valida um requisito específico.

        Args:
            dados_analise: Dados a validar
            norma_codigo: Código da norma
            requisito: Requisito a validar

        Returns:
            True se conforme, False caso contrário
        """
        # Regras de validação específicas
        if "documentação" in requisito.lower():
            return "documentacao" in dados_analise or "documentação" in dados_analise

        if "responsabilidades" in requisito.lower():
            return "responsabilidades" in dados_analise

        if "controle" in requisito.lower():
            return "controles" in dados_analise or "controle" in dados_analise

        if "política" in requisito.lower():
            return "politica" in dados_analise or "política" in dados_analise

        if "segurança" in requisito.lower():
            return "seguranca" in dados_analise or "segurança" in dados_analise

        if "risco" in requisito.lower():
            return "risco" in dados_analise or "riscos" in dados_analise

        # Por padrão, considerar conforme se dados existem
        return len(dados_analise) > 0

    def _calcular_conformidade_ponderada(
        self,
        conformidade_por_norma: Dict[str, float],
        normas_aplicaveis: List[str],
    ) -> float:
        """
        Calcula conformidade geral ponderada.

        Args:
            conformidade_por_norma: Conformidade por norma
            normas_aplicaveis: Normas aplicáveis

        Returns:
            Conformidade geral ponderada (0-100)
        """
        if not normas_aplicaveis:
            return 0.0

        conformidade_total = 0.0
        peso_total = 0.0

        for norma_codigo in normas_aplicaveis:
            if norma_codigo in self.normas_registradas:
                peso = self.normas_registradas[norma_codigo].get("peso", 0.1)
                conformidade = conformidade_por_norma.get(norma_codigo, 0.0)
                conformidade_total += conformidade * peso
                peso_total += peso

        if peso_total > 0:
            return conformidade_total / peso_total
        return 0.0

    def obter_historico_validacoes(self) -> List[ResultadoValidacao]:
        """Retorna histórico de validações."""
        return self.historico_validacoes.copy()

    def gerar_relatorio_conformidade(
        self, resultado: ResultadoValidacao
    ) -> Dict[str, Any]:
        """
        Gera relatório de conformidade.

        Args:
            resultado: Resultado da validação

        Returns:
            Dicionário com relatório estruturado
        """
        return {
            "conformidade_geral": resultado.conformidade_geral,
            "status": resultado.status_geral.value,
            "normas_aplicaveis": resultado.normas_aplicaveis,
            "conformidade_por_norma": resultado.conformidade_por_norma,
            "total_achados": len(resultado.achados),
            "achados_criticos": len([a for a in resultado.achados if a.severidade == "crítica"]),
            "achados_altos": len([a for a in resultado.achados if a.severidade == "alta"]),
            "achados_medios": len([a for a in resultado.achados if a.severidade == "média"]),
            "achados_baixos": len([a for a in resultado.achados if a.severidade == "baixa"]),
            "inconsistencias": resultado.inconsistencias,
            "timestamp": resultado.timestamp.isoformat(),
        }


# Instância global do validador
validador = ValidadorConformidade()
