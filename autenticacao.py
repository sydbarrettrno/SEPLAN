"""
Endpoints de Autenticação
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa endpoints para login, registro, logout e gerenciamento de sessões.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime, timedelta
from typing import Optional

from api.auth.security import (
    GerenciadorJWT,
    gerenciador_jwt,
    gerenciador_sessao,
    auditoria_acesso,
    controlador_acesso,
    Papel,
    TipoToken,
)
from api.auth.usuarios import gerenciador_usuarios
from api.auth.models import (
    LoginRequest,
    LoginResponse,
    RegistroRequest,
    RegistroResponse,
    TokenResponse,
    UsuarioResponse,
    AlterarSenhaRequest,
    PermissoesResponse,
    ErrorAuthResponse,
)
from api.config import config
from api.utils import gerador_id, logger_sistema


router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


# ============================================================================
# Dependências
# ============================================================================

async def obter_usuario_autenticado(request: Request):
    """Dependência para obter usuário autenticado."""
    # Extrair token do header
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = auth_header.replace("Bearer ", "")

    # Verificar token
    payload = gerenciador_jwt.verificar_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    usuario_id = payload.get("usuario_id")
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")

    return usuario


async def obter_usuario_admin(usuario = Depends(obter_usuario_autenticado)):
    """Dependência para verificar se é admin."""
    if usuario.papel != Papel.ADMIN:
        raise HTTPException(status_code=403, detail="Acesso negado. Privilégios de admin necessários.")
    return usuario


def _converter_usuario_response(usuario) -> UsuarioResponse:
    """Converte usuário interno para response."""
    return UsuarioResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        papel=usuario.papel,
        organizacao=usuario.organizacao,
        telefone=usuario.telefone,
        foto_perfil_url=usuario.foto_perfil_url,
        ativo=usuario.ativo,
        criado_em=usuario.criado_em,
        atualizado_em=usuario.atualizado_em,
        ultimo_login=usuario.ultimo_login,
    )


def _criar_token_response(usuario, request: Request) -> TokenResponse:
    """Cria response com tokens."""
    # Gerar tokens
    dados_token = {
        "usuario_id": usuario.id,
        "usuario_email": usuario.email,
        "papel": usuario.papel.value,
    }

    access_token = gerenciador_jwt.criar_token(
        dados_token,
        TipoToken.ACCESS,
        config.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    refresh_token = gerenciador_jwt.criar_token(
        dados_token,
        TipoToken.REFRESH,
        7 * 24 * 60,  # 7 dias
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        usuario=_converter_usuario_response(usuario),
    )


# ============================================================================
# Endpoints Públicos
# ============================================================================

@router.post(
    "/registro",
    response_model=RegistroResponse,
    summary="Registrar novo usuário",
)
async def registrar(requisicao: RegistroRequest):
    """
    Registra novo usuário no sistema.

    Args:
        requisicao: RegistroRequest com dados do usuário

    Returns:
        RegistroResponse com resultado

    Raises:
        HTTPException: Se email já existe
    """
    # Validar email duplicado
    if gerenciador_usuarios.obter_usuario_por_email(requisicao.email):
        raise HTTPException(status_code=400, detail="Email já registrado")

    # Criar usuário
    usuario = gerenciador_usuarios.criar_usuario(
        nome=requisicao.nome,
        email=requisicao.email,
        senha=requisicao.senha,
        papel=Papel.VISUALIZADOR,  # Papel padrão
        organizacao=requisicao.organizacao,
        telefone=requisicao.telefone,
        email_verificado=False,
    )

    if not usuario:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário")

    logger_sistema.log_analise_iniciada(f"Novo usuário: {requisicao.email}", "registro")

    return RegistroResponse(
        sucesso=True,
        mensagem="Usuário registrado com sucesso. Verifique seu email.",
        usuario=_converter_usuario_response(usuario),
        email_confirmacao_enviado=True,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login de usuário",
)
async def login(requisicao: LoginRequest, request: Request):
    """
    Autentica usuário com email e senha.

    Args:
        requisicao: LoginRequest com credenciais
        request: Requisição HTTP

    Returns:
        LoginResponse com tokens e dados do usuário

    Raises:
        HTTPException: Se credenciais inválidas
    """
    # Autenticar usuário
    usuario = gerenciador_usuarios.autenticar_usuario(
        requisicao.email,
        requisicao.senha,
    )

    if not usuario:
        # Registrar tentativa falha
        auditoria_acesso.registrar_erro_autenticacao(
            requisicao.email,
            request.client.host,
            "Credenciais inválidas",
        )

        logger_sistema.log_analise_erro(
            requisicao.email,
            "Falha de autenticação",
        )

        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    # Criar sessão
    sessao_id = gerenciador_sessao.criar_sessao(
        usuario.id,
        usuario.email,
        usuario.papel,
        request.client.host,
        request.headers.get("user-agent", ""),
    )

    # Registrar login bem-sucedido
    auditoria_acesso.registrar_login(
        usuario.id,
        usuario.email,
        request.client.host,
        sucesso=True,
    )

    logger_sistema.log_analise_iniciada(usuario.email, "login")

    # Criar tokens
    token_response = _criar_token_response(usuario, request)

    return LoginResponse(
        sucesso=True,
        mensagem=f"Bem-vindo, {usuario.nome}!",
        token=token_response,
        usuario=_converter_usuario_response(usuario),
    )


@router.post(
    "/renovar-token",
    response_model=TokenResponse,
    summary="Renovar access token",
)
async def renovar_token(request: Request):
    """
    Renova access token usando refresh token.

    Args:
        request: Requisição com refresh token no header

    Returns:
        TokenResponse com novo access token

    Raises:
        HTTPException: Se refresh token inválido
    """
    # Extrair refresh token
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Refresh token não fornecido")

    refresh_token = auth_header.replace("Bearer ", "")

    # Renovar token
    novo_access_token = gerenciador_jwt.renovar_token(refresh_token)

    if not novo_access_token:
        raise HTTPException(status_code=401, detail="Refresh token inválido ou expirado")

    # Decodificar para obter dados
    payload = gerenciador_jwt.verificar_token(refresh_token, TipoToken.REFRESH)
    usuario = gerenciador_usuarios.obter_usuario_por_id(payload["usuario_id"])

    return TokenResponse(
        access_token=novo_access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        usuario=_converter_usuario_response(usuario),
    )


# ============================================================================
# Endpoints Autenticados
# ============================================================================

@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obter dados do usuário autenticado",
)
async def obter_usuario_atual(usuario = Depends(obter_usuario_autenticado)):
    """Retorna dados do usuário autenticado."""
    return _converter_usuario_response(usuario)


@router.post(
    "/logout",
    summary="Fazer logout",
)
async def logout(
    request: Request,
    usuario = Depends(obter_usuario_autenticado),
):
    """
    Faz logout do usuário.

    Args:
        request: Requisição HTTP
        usuario: Usuário autenticado

    Returns:
        Mensagem de sucesso
    """
    # Registrar logout
    auditoria_acesso.registrar_logout(
        usuario.id,
        usuario.email,
        request.client.host,
    )

    logger_sistema.log_analise_concluida(usuario.email, 0)

    return {
        "sucesso": True,
        "mensagem": "Logout realizado com sucesso",
        "credito_autoral": "Criado por Eng. Anibal Nisgoski",
    }


@router.post(
    "/alterar-senha",
    summary="Alterar senha",
)
async def alterar_senha(
    requisicao: AlterarSenhaRequest,
    usuario = Depends(obter_usuario_autenticado),
):
    """
    Altera senha do usuário.

    Args:
        requisicao: AlterarSenhaRequest
        usuario: Usuário autenticado

    Returns:
        Mensagem de sucesso

    Raises:
        HTTPException: Se senhas não coincidem ou senha atual inválida
    """
    # Validar confirmação
    if requisicao.senha_nova != requisicao.confirmar_senha:
        raise HTTPException(status_code=400, detail="Senhas não coincidem")

    # Alterar senha
    if not gerenciador_usuarios.alterar_senha(
        usuario.id,
        requisicao.senha_atual,
        requisicao.senha_nova,
    ):
        raise HTTPException(status_code=400, detail="Senha atual inválida")

    return {
        "sucesso": True,
        "mensagem": "Senha alterada com sucesso",
    }


@router.get(
    "/permissoes",
    response_model=PermissoesResponse,
    summary="Obter permissões do usuário",
)
async def obter_permissoes(usuario = Depends(obter_usuario_autenticado)):
    """Retorna permissões do usuário."""
    permissoes = controlador_acesso.obter_permissoes(usuario.papel)

    return PermissoesResponse(
        usuario_id=usuario.id,
        papel=usuario.papel,
        permissoes=permissoes,
    )


@router.get(
    "/sessoes",
    summary="Listar sessões ativas",
)
async def listar_sessoes(usuario = Depends(obter_usuario_autenticado)):
    """Lista todas as sessões ativas do usuário."""
    sessoes = gerenciador_sessao.obter_sessoes_usuario(usuario.id)

    return {
        "total": len(sessoes),
        "sessoes": [
            {
                "id": s.get("id", ""),
                "ip_address": s.get("ip_address", ""),
                "criada_em": s.get("criada_em", ""),
                "ultima_atividade": s.get("ultima_atividade", ""),
            }
            for s in sessoes
        ],
    }


@router.post(
    "/sessoes/{sessao_id}/encerrar",
    summary="Encerrar sessão",
)
async def encerrar_sessao(
    sessao_id: str,
    usuario = Depends(obter_usuario_autenticado),
):
    """Encerra uma sessão específica."""
    # Verificar se sessão pertence ao usuário
    sessao = gerenciador_sessao.obter_sessao(sessao_id)

    if not sessao or sessao.get("usuario_id") != usuario.id:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")

    gerenciador_sessao.encerrar_sessao(sessao_id)

    return {
        "sucesso": True,
        "mensagem": "Sessão encerrada",
    }


# ============================================================================
# Endpoints Admin
# ============================================================================

@router.get(
    "/usuarios",
    summary="Listar usuários (Admin)",
)
async def listar_usuarios(
    papel: Optional[str] = None,
    ativo: Optional[bool] = None,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Lista todos os usuários (apenas admin)."""
    papel_enum = None
    if papel:
        try:
            papel_enum = Papel(papel)
        except ValueError:
            raise HTTPException(status_code=400, detail="Papel inválido")

    usuarios = gerenciador_usuarios.listar_usuarios(papel_enum, ativo)

    return {
        "total": len(usuarios),
        "usuarios": [_converter_usuario_response(u) for u in usuarios],
    }


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obter dados de usuário (Admin)",
)
async def obter_usuario(
    usuario_id: str,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Obtém dados de um usuário específico (apenas admin)."""
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return _converter_usuario_response(usuario)


@router.post(
    "/usuarios/{usuario_id}/papel",
    summary="Alterar papel de usuário (Admin)",
)
async def alterar_papel_usuario(
    usuario_id: str,
    novo_papel: str,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Altera papel de um usuário (apenas admin)."""
    try:
        papel_enum = Papel(novo_papel)
    except ValueError:
        raise HTTPException(status_code=400, detail="Papel inválido")

    if not gerenciador_usuarios.alterar_papel(usuario_id, papel_enum):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {
        "sucesso": True,
        "mensagem": f"Papel alterado para {novo_papel}",
    }


@router.post(
    "/usuarios/{usuario_id}/desativar",
    summary="Desativar usuário (Admin)",
)
async def desativar_usuario(
    usuario_id: str,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Desativa um usuário (apenas admin)."""
    if not gerenciador_usuarios.desativar_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {
        "sucesso": True,
        "mensagem": "Usuário desativado",
    }


@router.post(
    "/usuarios/{usuario_id}/ativar",
    summary="Ativar usuário (Admin)",
)
async def ativar_usuario(
    usuario_id: str,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Ativa um usuário (apenas admin)."""
    if not gerenciador_usuarios.ativar_usuario(usuario_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return {
        "sucesso": True,
        "mensagem": "Usuário ativado",
    }


@router.get(
    "/auditoria",
    summary="Obter registros de auditoria (Admin)",
)
async def obter_auditoria(
    usuario_id: Optional[str] = None,
    tipo: Optional[str] = None,
    limite: int = 100,
    usuario_admin = Depends(obter_usuario_admin),
):
    """Obtém registros de auditoria (apenas admin)."""
    registros = auditoria_acesso.obter_registros(usuario_id, tipo, limite)

    return {
        "total": len(registros),
        "registros": registros,
    }


@router.get(
    "/estatisticas",
    summary="Obter estatísticas (Admin)",
)
async def obter_estatisticas(usuario_admin = Depends(obter_usuario_admin)):
    """Obtém estatísticas do sistema (apenas admin)."""
    return {
        "usuarios": gerenciador_usuarios.obter_estatisticas(),
        "sessoes": gerenciador_sessao.obter_estatisticas(),
        "auditoria": auditoria_acesso.obter_estatisticas(),
        "credito_autoral": "Criado por Eng. Anibal Nisgoski",
    }
