"""
Configuração do Backend FastAPI
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski
"""

import os
from typing import Optional


class Config:
    """Configuração base da aplicação."""

    # Informações da aplicação
    APP_NAME = "Sistema Analítico de IA"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "Eng. Anibal Nisgoski"
    APP_DESCRIPTION = "Sistema Analítico de IA com RAG, Regras Determinísticas e Relatórios ABNT"

    # Ambiente
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"

    # Servidor
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", 8000))

    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    # Banco de dados
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/sistema_analitico"
    )

    # Redis (para cache e fila)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Banco vetorial (Qdrant)
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME = "sistema_analitico_embeddings"

    # LLM (OpenAI ou compatível)
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

    # Segurança
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # KPIs alvo
    KPI_CONFORMIDADE_MIN = 0.95  # 95%
    KPI_CONFIABILIDADE_MIN = 0.90  # 90%
    KPI_TEMPO_MAX_SEGUNDOS = 10  # 10 segundos
    KPI_CLAREZA_MIN = 8.0  # 8/10
    KPI_COBERTURA_MIN = 1.0  # 100%

    # Configurações de análise
    TAMANHO_MAXIMO_DOCUMENTO = 10 * 1024 * 1024  # 10 MB
    LIMITE_CHUNKS_BUSCA = 5
    LIMITE_SIMILARIDADE_RAG = 0.3

    # Configurações de relatório
    USAR_TEMPLATE_ABNT = True
    INCLUIR_CREDITO_AUTORAL = True
    CREDITO_AUTORAL = f"Criado por {APP_AUTHOR}"

    @classmethod
    def get_config(cls) -> "Config":
        """Retorna instância de configuração."""
        return cls()


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    ENVIRONMENT = "development"
    DEBUG = True


class ProductionConfig(Config):
    """Configuração para produção."""
    ENVIRONMENT = "production"
    DEBUG = False


class TestingConfig(Config):
    """Configuração para testes."""
    ENVIRONMENT = "testing"
    DEBUG = True
    DATABASE_URL = "sqlite:///test.db"
    REDIS_URL = "redis://localhost:6379/1"


def get_config() -> Config:
    """Retorna configuração apropriada baseada no ambiente."""
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Instância global de configuração
config = get_config()
