"""
Aplicação Principal FastAPI
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Ponto de entrada da API backend com todos os endpoints.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from api.config import config
from api.models import (
    AnaliseRequest,
    AnaliseResponse,
    DocumentoRAGRequest,
    DocumentoRAGResponse,
    BuscaRAGRequest,
    BuscaRAGResponse,
    EstatisticasRAGResponse,
    HealthCheckResponse,
    ErrorResponse,
)
from api.endpoints.analisar import processador
from api.endpoints.autenticacao import router as auth_router
from api.endpoints.admin import router as admin_router
from api.rag.manager import gerenciador_rag, TipoDocumento
from api.utils import logger_sistema, gerador_id


# Configurar logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifecycle Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia lifecycle da aplicação."""
    # Startup
    logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Ambiente: {config.ENVIRONMENT}")
    logger.info(f"Debug: {config.DEBUG}")

    # Inicializar componentes
    logger.info("Inicializando componentes...")

    yield

    # Shutdown
    logger.info("Encerrando aplicação...")


# ============================================================================
# Criar Aplicação FastAPI
# ============================================================================

app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    lifespan=lifespan,
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=config.CORS_ALLOW_CREDENTIALS,
    allow_methods=config.CORS_ALLOW_METHODS,
    allow_headers=config.CORS_ALLOW_HEADERS,
)

# ============================================================================
# Incluir Routers
# ============================================================================

app.include_router(auth_router)
app.include_router(admin_router)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse, tags=["Sistema"])
async def health_check():
    """
    Verifica saúde da aplicação.

    Returns:
        HealthCheckResponse com status dos componentes
    """
    return HealthCheckResponse(
        status="operacional",
        versao=config.APP_VERSION,
        autor=config.APP_AUTHOR,
        timestamp=datetime.utcnow(),
        componentes={
            "api": "ok",
            "rag": "ok",
            "calc": "ok",
            "rules": "ok",
        },
    )


# ============================================================================
# Endpoints de Análise
# ============================================================================

@app.post(
    "/api/analisar",
    response_model=AnaliseResponse,
    tags=["Análise"],
    summary="Executar análise completa",
)
async def analisar(requisicao: AnaliseRequest, background_tasks: BackgroundTasks):
    """
    Executa análise técnico-normativa completa.

    Fluxo:
    1. Classifica intenção da análise
    2. Valida dados mínimos
    3. Executa funções determinísticas
    4. Busca contexto no RAG
    5. Compõe parecer estruturado
    6. Gera relatório ABNT

    Args:
        requisicao: AnaliseRequest com dados da análise

    Returns:
        AnaliseResponse com resultado completo

    Raises:
        HTTPException: Se houver erro no processamento
    """
    try:
        logger_sistema.log_analise_iniciada(
            requisicao.titulo, requisicao.tipo_analise.value
        )

        # Processar análise
        resultado = await processador.processar_analise(requisicao)

        logger_sistema.log_analise_concluida(
            resultado.id, resultado.metricas.tempo_processamento_ms
        )

        return resultado

    except ValueError as e:
        logger_sistema.log_analise_erro(requisicao.titulo, str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger_sistema.log_analise_erro(requisicao.titulo, str(e))
        raise HTTPException(status_code=500, detail="Erro ao processar análise")


@app.get(
    "/api/analises/{analise_id}",
    response_model=dict,
    tags=["Análise"],
    summary="Obter análise por ID",
)
async def obter_analise(analise_id: str):
    """
    Obtém resultado de análise anterior.

    Args:
        analise_id: ID da análise

    Returns:
        Resultado da análise

    Raises:
        HTTPException: Se análise não encontrada
    """
    resultado = processador.obter_analise(analise_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return resultado


@app.get(
    "/api/analises",
    response_model=list,
    tags=["Análise"],
    summary="Listar todas as análises",
)
async def listar_analises():
    """
    Lista todas as análises realizadas.

    Returns:
        Lista de análises
    """
    return processador.listar_analises()


# ============================================================================
# Endpoints de RAG
# ============================================================================

@app.post(
    "/api/rag/ingerir",
    response_model=DocumentoRAGResponse,
    tags=["RAG"],
    summary="Ingerir documento no RAG",
)
async def ingerir_documento(requisicao: DocumentoRAGRequest):
    """
    Ingere novo documento no sistema RAG.

    Args:
        requisicao: DocumentoRAGRequest com dados do documento

    Returns:
        DocumentoRAGResponse com documento criado

    Raises:
        HTTPException: Se houver erro na ingestion
    """
    try:
        tipo_doc = TipoDocumento(requisicao.tipo)
        documento = gerenciador_rag.ingerir_documento(
            titulo=requisicao.titulo,
            conteudo=requisicao.conteudo,
            tipo=tipo_doc,
            fonte=requisicao.fonte,
            tags=requisicao.tags,
            metadados=requisicao.metadados,
        )

        logger_sistema.log_documento_ingerido(documento.id, documento.titulo)

        return DocumentoRAGResponse(
            id=documento.id,
            titulo=documento.titulo,
            tipo=documento.tipo.value,
            fonte=documento.fonte,
            data_criacao=documento.data_criacao,
            data_atualizacao=documento.data_atualizacao,
            tags=documento.tags,
            total_chunks=len([
                c for c in gerenciador_rag.chunks.values()
                if c.documento_id == documento.id
            ]),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger_sistema.log_erro_sistema("RAG", str(e))
        raise HTTPException(status_code=500, detail="Erro ao ingerir documento")


@app.post(
    "/api/rag/buscar",
    response_model=BuscaRAGResponse,
    tags=["RAG"],
    summary="Buscar no RAG",
)
async def buscar_rag(requisicao: BuscaRAGRequest):
    """
    Busca documentos no sistema RAG.

    Args:
        requisicao: BuscaRAGRequest com query de busca

    Returns:
        BuscaRAGResponse com resultados

    Raises:
        HTTPException: Se houver erro na busca
    """
    try:
        tipo_doc = None
        if requisicao.tipo_documento:
            tipo_doc = TipoDocumento(requisicao.tipo_documento)

        resultado = gerenciador_rag.buscar(
            query=requisicao.query,
            tipo_documento=tipo_doc,
            limite=requisicao.limite,
        )

        logger_sistema.log_busca_rag(
            requisicao.query,
            resultado.total_resultados,
            resultado.tempo_busca_ms,
        )

        from api.models import ChunkRAGResponse

        return BuscaRAGResponse(
            chunks=[
                ChunkRAGResponse(
                    id=chunk.id,
                    documento_id=chunk.documento_id,
                    conteudo=chunk.conteudo,
                    numero_sequencia=chunk.numero_sequencia,
                    score_similaridade=score,
                )
                for chunk, score in zip(
                    resultado.chunks, resultado.scores_similaridade
                )
            ],
            documentos_relacionados=[
                DocumentoRAGResponse(
                    id=doc.id,
                    titulo=doc.titulo,
                    tipo=doc.tipo.value,
                    fonte=doc.fonte,
                    data_criacao=doc.data_criacao,
                    data_atualizacao=doc.data_atualizacao,
                    tags=doc.tags,
                    total_chunks=len([
                        c for c in gerenciador_rag.chunks.values()
                        if c.documento_id == doc.id
                    ]),
                )
                for doc in resultado.documentos_relacionados
            ],
            tempo_busca_ms=resultado.tempo_busca_ms,
            total_resultados=resultado.total_resultados,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger_sistema.log_erro_sistema("RAG", str(e))
        raise HTTPException(status_code=500, detail="Erro ao buscar no RAG")


@app.get(
    "/api/rag/documentos",
    response_model=list,
    tags=["RAG"],
    summary="Listar documentos no RAG",
)
async def listar_documentos_rag(tipo: str = None):
    """
    Lista documentos no RAG.

    Args:
        tipo: Filtrar por tipo (opcional)

    Returns:
        Lista de documentos
    """
    tipo_doc = None
    if tipo:
        try:
            tipo_doc = TipoDocumento(tipo)
        except ValueError:
            raise HTTPException(status_code=400, detail="Tipo de documento inválido")

    documentos = gerenciador_rag.listar_documentos(tipo=tipo_doc)

    return [
        DocumentoRAGResponse(
            id=doc.id,
            titulo=doc.titulo,
            tipo=doc.tipo.value,
            fonte=doc.fonte,
            data_criacao=doc.data_criacao,
            data_atualizacao=doc.data_atualizacao,
            tags=doc.tags,
            total_chunks=len([
                c for c in gerenciador_rag.chunks.values()
                if c.documento_id == doc.id
            ]),
        )
        for doc in documentos
    ]


@app.get(
    "/api/rag/estatisticas",
    response_model=EstatisticasRAGResponse,
    tags=["RAG"],
    summary="Obter estatísticas do RAG",
)
async def obter_estatisticas_rag():
    """
    Obtém estatísticas do sistema RAG.

    Returns:
        EstatisticasRAGResponse com estatísticas
    """
    stats = gerenciador_rag.obter_estatisticas()
    return EstatisticasRAGResponse(**stats)


# ============================================================================
# Error Handler
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais."""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================================
# Root
# ============================================================================

@app.get("/", tags=["Sistema"])
async def root():
    """Raiz da API."""
    return {
        "nome": config.APP_NAME,
        "versao": config.APP_VERSION,
        "autor": config.APP_AUTHOR,
        "descricao": config.APP_DESCRIPTION,
        "credito": "Criado por Eng. Anibal Nisgoski",
        "endpoints": {
            "health": "/health",
            "analise": "/api/analisar",
            "rag": "/api/rag/buscar",
            "docs": "/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
