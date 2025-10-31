"""
Utilitários do Sistema Analítico de IA
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class GeradorID:
    """Gerador de IDs únicos."""

    @staticmethod
    def gerar_id_analise() -> str:
        """Gera ID único para análise."""
        return f"analise_{str(uuid.uuid4())[:8]}"

    @staticmethod
    def gerar_id_documento() -> str:
        """Gera ID único para documento."""
        return f"doc_{str(uuid.uuid4())[:8]}"

    @staticmethod
    def gerar_id_relatorio() -> str:
        """Gera ID único para relatório."""
        return f"rel_{str(uuid.uuid4())[:8]}"

    @staticmethod
    def gerar_id_sessao() -> str:
        """Gera ID único para sessão."""
        return f"sess_{str(uuid.uuid4())[:8]}"


class ValidadorDados:
    """Validador de dados de entrada."""

    @staticmethod
    def validar_texto(texto: str, minimo: int = 1, maximo: Optional[int] = None) -> bool:
        """Valida texto."""
        if not isinstance(texto, str):
            return False
        if len(texto.strip()) < minimo:
            return False
        if maximo and len(texto) > maximo:
            return False
        return True

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida email."""
        import re
        padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(padrao, email) is not None

    @staticmethod
    def validar_url(url: str) -> bool:
        """Valida URL."""
        import re
        padrao = r"^https?://[^\s/$.?#].[^\s]*$"
        return re.match(padrao, url) is not None

    @staticmethod
    def validar_json(dados: str) -> bool:
        """Valida JSON."""
        try:
            json.loads(dados)
            return True
        except (json.JSONDecodeError, TypeError):
            return False


class FormatadorSaida:
    """Formatador de saída de dados."""

    @staticmethod
    def formatar_percentual(valor: float, casas_decimais: int = 2) -> str:
        """Formata valor como percentual."""
        return f"{valor:.{casas_decimais}f}%"

    @staticmethod
    def formatar_tempo_ms(tempo_ms: float) -> str:
        """Formata tempo em ms."""
        if tempo_ms < 1000:
            return f"{tempo_ms:.0f}ms"
        elif tempo_ms < 60000:
            return f"{tempo_ms / 1000:.2f}s"
        else:
            return f"{tempo_ms / 60000:.2f}min"

    @staticmethod
    def formatar_tamanho_bytes(tamanho: int) -> str:
        """Formata tamanho em bytes."""
        for unidade in ["B", "KB", "MB", "GB"]:
            if tamanho < 1024:
                return f"{tamanho:.2f}{unidade}"
            tamanho /= 1024
        return f"{tamanho:.2f}TB"

    @staticmethod
    def formatar_data(data: datetime, formato: str = "%d/%m/%Y %H:%M:%S") -> str:
        """Formata data."""
        return data.strftime(formato)

    @staticmethod
    def formatar_indice(valor: float, maximo: float = 100) -> str:
        """Formata índice com barra visual."""
        percentual = (valor / maximo) * 100
        barras = int(percentual / 10)
        return f"[{'█' * barras}{'░' * (10 - barras)}] {valor:.1f}/{maximo:.1f}"


class LoggerSistema:
    """Logger centralizado do sistema."""

    @staticmethod
    def log_analise_iniciada(analise_id: str, tipo: str) -> None:
        """Log de análise iniciada."""
        logger.info(f"Análise iniciada: {analise_id} (tipo: {tipo})")

    @staticmethod
    def log_analise_concluida(analise_id: str, tempo_ms: float) -> None:
        """Log de análise concluída."""
        logger.info(f"Análise concluída: {analise_id} (tempo: {tempo_ms:.0f}ms)")

    @staticmethod
    def log_analise_erro(analise_id: str, erro: str) -> None:
        """Log de erro em análise."""
        logger.error(f"Erro em análise {analise_id}: {erro}")

    @staticmethod
    def log_documento_ingerido(doc_id: str, titulo: str) -> None:
        """Log de documento ingerido."""
        logger.info(f"Documento ingerido: {doc_id} ({titulo})")

    @staticmethod
    def log_busca_rag(query: str, resultados: int, tempo_ms: float) -> None:
        """Log de busca no RAG."""
        logger.info(f"Busca RAG: '{query}' ({resultados} resultados em {tempo_ms:.0f}ms)")

    @staticmethod
    def log_erro_sistema(modulo: str, erro: str) -> None:
        """Log de erro do sistema."""
        logger.error(f"Erro em {modulo}: {erro}")


class CacheSimples:
    """Cache simples em memória."""

    def __init__(self, ttl_segundos: int = 3600):
        """Inicializa cache."""
        self.dados: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_segundos

    def obter(self, chave: str) -> Optional[Any]:
        """Obtém valor do cache."""
        if chave not in self.dados:
            return None

        item = self.dados[chave]
        if datetime.utcnow().timestamp() - item["timestamp"] > self.ttl:
            del self.dados[chave]
            return None

        return item["valor"]

    def armazenar(self, chave: str, valor: Any) -> None:
        """Armazena valor no cache."""
        self.dados[chave] = {
            "valor": valor,
            "timestamp": datetime.utcnow().timestamp(),
        }

    def limpar(self) -> None:
        """Limpa cache."""
        self.dados.clear()

    def obter_estatisticas(self) -> Dict[str, int]:
        """Retorna estatísticas do cache."""
        return {
            "total_itens": len(self.dados),
            "tamanho_aproximado_bytes": sum(
                len(str(item["valor"]).encode())
                for item in self.dados.values()
            ),
        }


class ConversorFormatos:
    """Conversor entre formatos de dados."""

    @staticmethod
    def dict_para_json(dados: Dict[str, Any]) -> str:
        """Converte dicionário para JSON."""
        return json.dumps(dados, ensure_ascii=False, indent=2)

    @staticmethod
    def json_para_dict(json_str: str) -> Dict[str, Any]:
        """Converte JSON para dicionário."""
        return json.loads(json_str)

    @staticmethod
    def dict_para_csv_linha(dados: Dict[str, Any]) -> str:
        """Converte dicionário para linha CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=dados.keys())
        writer.writerow(dados)
        return output.getvalue().strip()


# Instâncias globais
gerador_id = GeradorID()
validador = ValidadorDados()
formatador = FormatadorSaida()
logger_sistema = LoggerSistema()
cache = CacheSimples()
conversor = ConversorFormatos()
