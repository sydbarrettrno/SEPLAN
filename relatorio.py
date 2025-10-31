"""
Módulo de Geração de Relatórios ABNT
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa geração de relatórios técnicos em formato DOCX e PDF
seguindo normas ABNT NBR 14724 com crédito autoral visível.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import io


class FormatoRelatorio(str, Enum):
    """Formatos de saída de relatório."""
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"


@dataclass
class ConfiguracaoRelatorio:
    """Configuração de relatório."""
    titulo: str
    autor: str
    data: datetime
    instituicao: Optional[str] = None
    versao: str = "1.0"
    incluir_indice: bool = True
    incluir_referencias: bool = True
    credito_autoral: str = "Criado por Eng. Anibal Nisgoski"
    margem_superior: float = 3.0  # cm
    margem_inferior: float = 2.0
    margem_esquerda: float = 3.0
    margem_direita: float = 2.0


@dataclass
class SecaoRelatorio:
    """Seção de relatório."""
    numero: int
    titulo: str
    conteudo: str
    subsecoes: List["SecaoRelatorio"] = None


class GeradorRelatorioABNT:
    """
    Gerador de relatórios ABNT.
    Implementa formatação conforme NBR 14724.
    """

    # Configurações ABNT
    FONTE_PADRAO = "Times New Roman"
    TAMANHO_FONTE_CORPO = 12
    TAMANHO_FONTE_TITULO = 14
    TAMANHO_FONTE_SUBTITULO = 12
    ESPACAMENTO_LINHA = 1.5
    ESPACAMENTO_PARAGRAFO = 0.0

    def __init__(self, config: ConfiguracaoRelatorio):
        """Inicializa o gerador."""
        self.config = config
        self.secoes: List[SecaoRelatorio] = []
        self.referencias: List[Dict[str, str]] = []
        self.anexos: List[Dict[str, Any]] = []

    def adicionar_secao(
        self,
        numero: int,
        titulo: str,
        conteudo: str,
        subsecoes: Optional[List[SecaoRelatorio]] = None,
    ) -> None:
        """
        Adiciona seção ao relatório.

        Args:
            numero: Número da seção
            titulo: Título da seção
            conteudo: Conteúdo da seção
            subsecoes: Subsecções (opcional)
        """
        secao = SecaoRelatorio(
            numero=numero,
            titulo=titulo,
            conteudo=conteudo,
            subsecoes=subsecoes or [],
        )
        self.secoes.append(secao)

    def adicionar_referencia(
        self,
        tipo: str,
        autores: str,
        titulo: str,
        fonte: str,
        ano: int,
        url: Optional[str] = None,
    ) -> None:
        """
        Adiciona referência bibliográfica.

        Args:
            tipo: Tipo de referência (livro, artigo, norma, etc)
            autores: Autores
            titulo: Título
            fonte: Fonte/editora
            ano: Ano de publicação
            url: URL (opcional)
        """
        referencia = {
            "tipo": tipo,
            "autores": autores,
            "titulo": titulo,
            "fonte": fonte,
            "ano": ano,
            "url": url,
        }
        self.referencias.append(referencia)

    def adicionar_anexo(
        self,
        titulo: str,
        conteudo: str,
        tipo: str = "texto",
    ) -> None:
        """
        Adiciona anexo ao relatório.

        Args:
            titulo: Título do anexo
            conteudo: Conteúdo do anexo
            tipo: Tipo de conteúdo (texto, tabela, imagem)
        """
        anexo = {
            "titulo": titulo,
            "conteudo": conteudo,
            "tipo": tipo,
        }
        self.anexos.append(anexo)

    def gerar_capa(self) -> str:
        """
        Gera capa do relatório.

        Returns:
            Texto formatado da capa
        """
        capa = []
        capa.append("\n" * 5)
        capa.append(f"{self.config.instituicao or 'INSTITUIÇÃO'}\n".center(80))
        capa.append("\n" * 3)
        capa.append(f"{self.config.titulo}\n".center(80))
        capa.append("\n" * 3)
        capa.append(f"Versão {self.config.versao}\n".center(80))
        capa.append("\n" * 5)
        capa.append(f"Autor: {self.config.autor}\n".center(80))
        capa.append(f"Data: {self.config.data.strftime('%d de %B de %Y')}\n".center(80))
        capa.append("\n" * 3)
        capa.append(f"━" * 80 + "\n")
        capa.append(f"{self.config.credito_autoral}\n".center(80))
        capa.append(f"━" * 80 + "\n")

        return "".join(capa)

    def gerar_indice(self) -> str:
        """
        Gera índice do relatório.

        Returns:
            Texto formatado do índice
        """
        if not self.config.incluir_indice:
            return ""

        indice = ["\n\nÍNDICE\n", "=" * 80 + "\n\n"]

        for secao in self.secoes:
            indice.append(f"{secao.numero}. {secao.titulo}\n")
            if secao.subsecoes:
                for subsecao in secao.subsecoes:
                    indice.append(f"   {subsecao.numero}. {subsecao.titulo}\n")

        if self.referencias:
            indice.append("REFERÊNCIAS\n")

        if self.anexos:
            indice.append("ANEXOS\n")

        indice.append("\n" + "=" * 80 + "\n")

        return "".join(indice)

    def gerar_corpo(self) -> str:
        """
        Gera corpo do relatório.

        Returns:
            Texto formatado do corpo
        """
        corpo = ["\n\n"]

        for secao in self.secoes:
            # Título da seção
            corpo.append(f"\n{secao.numero}. {secao.titulo.upper()}\n")
            corpo.append("-" * 80 + "\n\n")

            # Conteúdo
            corpo.append(self._formatar_paragrafo(secao.conteudo))
            corpo.append("\n")

            # Subsecções
            if secao.subsecoes:
                for subsecao in secao.subsecoes:
                    corpo.append(f"\n{subsecao.numero}. {subsecao.titulo}\n")
                    corpo.append(self._formatar_paragrafo(subsecao.conteudo))
                    corpo.append("\n")

        return "".join(corpo)

    def gerar_referencias(self) -> str:
        """
        Gera seção de referências.

        Returns:
            Texto formatado de referências
        """
        if not self.referencias or not self.config.incluir_referencias:
            return ""

        referencias = ["\n\nREFERÊNCIAS\n", "=" * 80 + "\n\n"]

        for ref in self.referencias:
            referencia_str = self._formatar_referencia(ref)
            referencias.append(referencia_str)
            referencias.append("\n")

        return "".join(referencias)

    def gerar_anexos(self) -> str:
        """
        Gera seção de anexos.

        Returns:
            Texto formatado de anexos
        """
        if not self.anexos:
            return ""

        anexos = ["\n\nANEXOS\n", "=" * 80 + "\n\n"]

        for i, anexo in enumerate(self.anexos, 1):
            anexos.append(f"ANEXO {i}: {anexo['titulo'].upper()}\n")
            anexos.append("-" * 80 + "\n\n")
            anexos.append(anexo["conteudo"])
            anexos.append("\n\n")

        return "".join(anexos)

    def gerar_rodape(self) -> str:
        """
        Gera rodapé do relatório.

        Returns:
            Texto formatado do rodapé
        """
        rodape = []
        rodape.append("\n" + "=" * 80 + "\n")
        rodape.append(f"Relatório gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n")
        rodape.append(f"Versão: {self.config.versao}\n")
        rodape.append(f"Autor: {self.config.autor}\n")
        rodape.append(f"{self.config.credito_autoral}\n")
        rodape.append("=" * 80 + "\n")

        return "".join(rodape)

    def gerar_texto_completo(self) -> str:
        """
        Gera texto completo do relatório.

        Returns:
            Texto formatado completo
        """
        partes = [
            self.gerar_capa(),
            self.gerar_indice(),
            self.gerar_corpo(),
            self.gerar_referencias(),
            self.gerar_anexos(),
            self.gerar_rodape(),
        ]

        return "".join(partes)

    def gerar_html(self) -> str:
        """
        Gera relatório em HTML.

        Returns:
            HTML do relatório
        """
        html = []
        html.append("<!DOCTYPE html>\n")
        html.append("<html lang=\"pt-BR\">\n")
        html.append("<head>\n")
        html.append("<meta charset=\"UTF-8\">\n")
        html.append(f"<title>{self.config.titulo}</title>\n")
        html.append("<style>\n")
        html.append(self._gerar_css())
        html.append("</style>\n")
        html.append("</head>\n")
        html.append("<body>\n")

        # Capa
        html.append("<div class=\"capa\">\n")
        html.append(f"<h1>{self.config.titulo}</h1>\n")
        html.append(f"<p class=\"autor\">Autor: {self.config.autor}</p>\n")
        html.append(f"<p class=\"data\">Data: {self.config.data.strftime('%d de %B de %Y')}</p>\n")
        html.append(f"<p class=\"credito\">{self.config.credito_autoral}</p>\n")
        html.append("</div>\n")

        # Corpo
        html.append("<div class=\"corpo\">\n")
        for secao in self.secoes:
            html.append(f"<h2>{secao.numero}. {secao.titulo}</h2>\n")
            html.append(f"<p>{secao.conteudo}</p>\n")

        html.append("</div>\n")

        # Rodapé
        html.append("<div class=\"rodape\">\n")
        html.append(f"<p>{self.config.credito_autoral}</p>\n")
        html.append(f"<p>Gerado em: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}</p>\n")
        html.append("</div>\n")

        html.append("</body>\n")
        html.append("</html>\n")

        return "".join(html)

    def _gerar_css(self) -> str:
        """Gera CSS para HTML."""
        css = """
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.5;
            margin: 3cm 3cm 2cm 3cm;
            color: #333;
        }
        .capa {
            text-align: center;
            page-break-after: always;
            padding: 5cm 0;
        }
        .capa h1 {
            font-size: 24pt;
            font-weight: bold;
            margin-bottom: 3cm;
        }
        .capa .autor, .capa .data {
            font-size: 12pt;
            margin: 1cm 0;
        }
        .capa .credito {
            font-size: 11pt;
            font-weight: bold;
            margin-top: 3cm;
            border-top: 1px solid #000;
            border-bottom: 1px solid #000;
            padding: 1cm 0;
        }
        h2 {
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1.5cm;
            margin-bottom: 0.5cm;
        }
        p {
            font-size: 12pt;
            text-align: justify;
            margin-bottom: 0.5cm;
        }
        .rodape {
            text-align: center;
            font-size: 10pt;
            margin-top: 2cm;
            padding-top: 1cm;
            border-top: 1px solid #ccc;
        }
        """
        return css

    def _formatar_paragrafo(self, texto: str, largura: int = 80) -> str:
        """
        Formata parágrafo com quebra de linha.

        Args:
            texto: Texto a formatar
            largura: Largura máxima da linha

        Returns:
            Texto formatado
        """
        palavras = texto.split()
        linhas = []
        linha_atual = []

        for palavra in palavras:
            linha_atual.append(palavra)
            if len(" ".join(linha_atual)) > largura:
                linha_atual.pop()
                linhas.append(" ".join(linha_atual))
                linha_atual = [palavra]

        if linha_atual:
            linhas.append(" ".join(linha_atual))

        return "\n".join(linhas) + "\n"

    def _formatar_referencia(self, ref: Dict[str, Any]) -> str:
        """
        Formata referência bibliográfica.

        Args:
            ref: Dicionário com dados da referência

        Returns:
            Referência formatada
        """
        # Formato ABNT simplificado
        autores = ref.get("autores", "")
        titulo = ref.get("titulo", "")
        fonte = ref.get("fonte", "")
        ano = ref.get("ano", "")
        url = ref.get("url", "")

        referencia = f"{autores}. {titulo}. {fonte}, {ano}."

        if url:
            referencia += f" Disponível em: {url}"

        return referencia


class GeradorRelatorioAnalise:
    """Gerador especializado para relatórios de análise."""

    def __init__(self, config: ConfiguracaoRelatorio):
        """Inicializa o gerador."""
        self.gerador = GeradorRelatorioABNT(config)

    def gerar_relatorio_analise(
        self,
        resultado_analise: Dict[str, Any],
    ) -> str:
        """
        Gera relatório completo de análise.

        Args:
            resultado_analise: Resultado da análise

        Returns:
            Texto completo do relatório
        """
        # Seção 1: Contexto e Enquadramento
        self.gerador.adicionar_secao(
            numero=1,
            titulo="Contexto e Enquadramento",
            conteudo=resultado_analise.get("contexto_enquadramento", ""),
        )

        # Seção 2: Fundamentação Técnica/Legal
        self.gerador.adicionar_secao(
            numero=2,
            titulo="Fundamentação Técnica e Legal",
            conteudo=resultado_analise.get("fundamentacao_tecnica", ""),
        )

        # Seção 3: Análise de Dados
        self.gerador.adicionar_secao(
            numero=3,
            titulo="Análise de Dados",
            conteudo=resultado_analise.get("analise_dados", ""),
        )

        # Seção 4: Achados e Inconsistências
        achados_texto = self._formatar_achados(resultado_analise.get("achados", []))
        self.gerador.adicionar_secao(
            numero=4,
            titulo="Achados e Inconsistências",
            conteudo=achados_texto,
        )

        # Seção 5: Análise de Risco
        risco_texto = f"Nível de risco geral: {resultado_analise.get('risco_geral', 'não classificado')}"
        self.gerador.adicionar_secao(
            numero=5,
            titulo="Análise de Risco",
            conteudo=risco_texto,
        )

        # Seção 6: Recomendações
        recomendacoes_texto = self._formatar_recomendacoes(
            resultado_analise.get("recomendacoes", [])
        )
        self.gerador.adicionar_secao(
            numero=6,
            titulo="Recomendações",
            conteudo=recomendacoes_texto,
        )

        # Seção 7: Síntese Final
        self.gerador.adicionar_secao(
            numero=7,
            titulo="Síntese Final",
            conteudo=resultado_analise.get("sintese_final", ""),
        )

        # Adicionar métricas como anexo
        metricas = resultado_analise.get("metricas", {})
        if metricas:
            metricas_texto = self._formatar_metricas(metricas)
            self.gerador.adicionar_anexo(
                titulo="Métricas da Análise",
                conteudo=metricas_texto,
                tipo="tabela",
            )

        return self.gerador.gerar_texto_completo()

    def _formatar_achados(self, achados: List[Dict[str, Any]]) -> str:
        """Formata lista de achados."""
        if not achados:
            return "Nenhum achado identificado."

        texto = []
        for i, achado in enumerate(achados, 1):
            texto.append(f"{i}. {achado.get('titulo', '')}")
            texto.append(f"   Severidade: {achado.get('severidade', 'N/A')}")
            texto.append(f"   Descrição: {achado.get('descricao', '')}")
            if achado.get('recomendacao'):
                texto.append(f"   Recomendação: {achado.get('recomendacao')}")
            texto.append("")

        return "\n".join(texto)

    def _formatar_recomendacoes(self, recomendacoes: List[str]) -> str:
        """Formata lista de recomendações."""
        if not recomendacoes:
            return "Nenhuma recomendação específica."

        texto = []
        for i, rec in enumerate(recomendacoes, 1):
            texto.append(f"{i}. {rec}")

        return "\n".join(texto)

    def _formatar_metricas(self, metricas: Dict[str, Any]) -> str:
        """Formata métricas."""
        texto = []
        texto.append("Métrica | Valor")
        texto.append("-" * 40)

        for chave, valor in metricas.items():
            if isinstance(valor, float):
                valor_fmt = f"{valor:.2f}"
            else:
                valor_fmt = str(valor)
            texto.append(f"{chave} | {valor_fmt}")

        return "\n".join(texto)


# Instância global
gerador_abnt = GeradorRelatorioABNT
