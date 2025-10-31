"""
Endpoints de Administração
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa endpoints para gerenciamento de usuários, papéis e permissões.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime

from api.auth.security import gerenciador_sessao, auditoria_acesso
from api.auth.usuarios import gerenciador_usuarios
from api.auth.papeis import gerenciador_papeis, PermissaoCategoria
from api.endpoints.autenticacao import obter_usuario_admin
from api.auth.models import UsuarioResponse


router = APIRouter(prefix="/api/admin", tags=["Administração"])


# ============================================================================
# Dependência para Admin
# ============================================================================

async def obter_admin(usuario = Depends(obter_usuario_admin)):
    """Dependência para verificar admin."""
    return usuario


# ============================================================================
# Endpoints de Usuários (Avançado)
# ============================================================================

@router.get(
    "/usuarios",
    summary="Listar usuários com filtros avançados",
)
async def listar_usuarios_avancado(
    papel: Optional[str] = Query(None, description="Filtrar por papel"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status"),
    email_verificado: Optional[bool] = Query(None, description="Filtrar por verificação"),
    busca: Optional[str] = Query(None, description="Buscar por nome ou email"),
    ordenar_por: str = Query("criado_em", description="Campo para ordenação"),
    ordem: str = Query("desc", description="Ordem (asc/desc)"),
    pagina: int = Query(1, ge=1, description="Número da página"),
    limite: int = Query(20, ge=1, le=100, description="Itens por página"),
    usuario_admin = Depends(obter_admin),
):
    """
    Lista usuários com filtros avançados e paginação.

    Args:
        papel: Filtrar por papel
        ativo: Filtrar por status ativo
        email_verificado: Filtrar por verificação
        busca: Buscar por nome ou email
        ordenar_por: Campo para ordenação
        ordem: Ordem de ordenação
        pagina: Número da página
        limite: Itens por página
        usuario_admin: Usuário admin autenticado

    Returns:
        Lista paginada de usuários com metadados
    """
    usuarios = list(gerenciador_usuarios.usuarios.values())

    # Aplicar filtros
    if papel:
        usuarios = [u for u in usuarios if u.papel.value == papel]

    if ativo is not None:
        usuarios = [u for u in usuarios if u.ativo == ativo]

    if email_verificado is not None:
        usuarios = [u for u in usuarios if u.email_verificado == email_verificado]

    if busca:
        busca_lower = busca.lower()
        usuarios = [
            u for u in usuarios
            if busca_lower in u.nome.lower() or busca_lower in u.email.lower()
        ]

    # Ordenar
    reverse = ordem.lower() == "desc"
    if ordenar_por == "nome":
        usuarios.sort(key=lambda u: u.nome, reverse=reverse)
    elif ordenar_por == "email":
        usuarios.sort(key=lambda u: u.email, reverse=reverse)
    elif ordenar_por == "criado_em":
        usuarios.sort(key=lambda u: u.criado_em, reverse=reverse)
    elif ordenar_por == "ultimo_login":
        usuarios.sort(key=lambda u: u.ultimo_login or datetime.min, reverse=reverse)

    # Paginar
    total = len(usuarios)
    inicio = (pagina - 1) * limite
    fim = inicio + limite
    usuarios_pagina = usuarios[inicio:fim]

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        "usuarios",
        "listar",
        True,
        {"filtros": {"papel": papel, "ativo": ativo}, "total": total},
    )

    return {
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": (total + limite - 1) // limite,
        "usuarios": [
            {
                "id": u.id,
                "nome": u.nome,
                "email": u.email,
                "papel": u.papel.value,
                "organizacao": u.organizacao,
                "ativo": u.ativo,
                "email_verificado": u.email_verificado,
                "criado_em": u.criado_em.isoformat(),
                "ultimo_login": u.ultimo_login.isoformat() if u.ultimo_login else None,
            }
            for u in usuarios_pagina
        ],
    }


@router.get(
    "/usuarios/{usuario_id}",
    summary="Obter detalhes completos de usuário",
)
async def obter_usuario_detalhes(
    usuario_id: str,
    usuario_admin = Depends(obter_admin),
):
    """Obtém detalhes completos de um usuário."""
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Obter sessões ativas
    sessoes = gerenciador_sessao.obter_sessoes_usuario(usuario_id)

    # Obter permissões do papel
    papel_obj = gerenciador_papeis.obter_papel(usuario.papel.value)
    permissoes = papel_obj.obter_permissoes() if papel_obj else []

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"usuario:{usuario_id}",
        "visualizar_detalhes",
        True,
    )

    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "papel": usuario.papel.value,
        "organizacao": usuario.organizacao,
        "telefone": usuario.telefone,
        "foto_perfil_url": usuario.foto_perfil_url,
        "ativo": usuario.ativo,
        "email_verificado": usuario.email_verificado,
        "tentativas_login_falha": usuario.tentativas_login_falha,
        "bloqueado_ate": usuario.bloqueado_ate.isoformat() if usuario.bloqueado_ate else None,
        "criado_em": usuario.criado_em.isoformat(),
        "atualizado_em": usuario.atualizado_em.isoformat(),
        "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None,
        "sessoes_ativas": len([s for s in sessoes if s.get("ativa")]),
        "papel_info": {
            "codigo": usuario.papel.value,
            "nome": papel_obj.nome if papel_obj else "",
            "permissoes": permissoes,
            "total_permissoes": len(permissoes),
        },
    }


@router.post(
    "/usuarios/{usuario_id}/atualizar",
    summary="Atualizar dados de usuário",
)
async def atualizar_usuario_admin(
    usuario_id: str,
    dados: dict,
    usuario_admin = Depends(obter_admin),
):
    """Atualiza dados de um usuário (admin)."""
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Campos permitidos
    campos_permitidos = {
        "nome",
        "organizacao",
        "telefone",
        "foto_perfil_url",
        "ativo",
        "email_verificado",
    }

    campos_atualizados = {}
    for campo, valor in dados.items():
        if campo in campos_permitidos:
            gerenciador_usuarios.atualizar_usuario(usuario_id, **{campo: valor})
            campos_atualizados[campo] = valor

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"usuario:{usuario_id}",
        "atualizar",
        True,
        {"campos": list(campos_atualizados.keys())},
    )

    return {
        "sucesso": True,
        "mensagem": "Usuário atualizado com sucesso",
        "campos_atualizados": campos_atualizados,
    }


@router.post(
    "/usuarios/{usuario_id}/resetar-senha",
    summary="Resetar senha de usuário",
)
async def resetar_senha_usuario(
    usuario_id: str,
    usuario_admin = Depends(obter_admin),
):
    """Reseta senha de um usuário gerando uma temporária."""
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Gerar senha temporária
    from api.auth.security import gerenciador_senha
    senha_temp = gerenciador_senha.gerar_senha_temporaria()

    # Resetar
    if not gerenciador_usuarios.resetar_senha(usuario_id, senha_temp):
        raise HTTPException(status_code=400, detail="Erro ao resetar senha")

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"usuario:{usuario_id}",
        "resetar_senha",
        True,
    )

    return {
        "sucesso": True,
        "mensagem": "Senha resetada com sucesso",
        "senha_temporaria": senha_temp,
        "aviso": "Compartilhe esta senha com segurança. O usuário deve alterá-la no primeiro login.",
    }


@router.post(
    "/usuarios/{usuario_id}/desbloquear",
    summary="Desbloquear usuário",
)
async def desbloquear_usuario(
    usuario_id: str,
    usuario_admin = Depends(obter_admin),
):
    """Desbloqueia um usuário bloqueado."""
    usuario = gerenciador_usuarios.obter_usuario_por_id(usuario_id)

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not usuario.bloqueado_ate:
        return {
            "sucesso": True,
            "mensagem": "Usuário não está bloqueado",
        }

    usuario.bloqueado_ate = None
    usuario.tentativas_login_falha = 0

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"usuario:{usuario_id}",
        "desbloquear",
        True,
    )

    return {
        "sucesso": True,
        "mensagem": "Usuário desbloqueado com sucesso",
    }


# ============================================================================
# Endpoints de Papéis e Permissões
# ============================================================================

@router.get(
    "/papeis",
    summary="Listar papéis",
)
async def listar_papeis(
    apenas_ativos: bool = Query(True, description="Apenas papéis ativos"),
    usuario_admin = Depends(obter_admin),
):
    """Lista papéis do sistema."""
    papeis = gerenciador_papeis.listar_papeis(apenas_ativos)

    return {
        "total": len(papeis),
        "papeis": [p.to_dict() for p in papeis],
    }


@router.get(
    "/papeis/{codigo_papel}",
    summary="Obter detalhes de papel",
)
async def obter_papel_detalhes(
    codigo_papel: str,
    usuario_admin = Depends(obter_admin),
):
    """Obtém detalhes completos de um papel."""
    papel = gerenciador_papeis.obter_papel(codigo_papel)

    if not papel:
        raise HTTPException(status_code=404, detail="Papel não encontrado")

    # Obter informações de permissões
    permissoes_info = []
    for codigo_perm in papel.obter_permissoes():
        perm = gerenciador_papeis.obter_permissao(codigo_perm)
        if perm:
            permissoes_info.append(perm.to_dict())

    return {
        **papel.to_dict(),
        "permissoes_detalhes": permissoes_info,
        "total_usuarios": len([
            u for u in gerenciador_usuarios.usuarios.values()
            if u.papel.value == codigo_papel
        ]),
    }


@router.post(
    "/papeis",
    summary="Criar papel customizado",
)
async def criar_papel(
    nome: str,
    descricao: str,
    permissoes: List[str],
    usuario_admin = Depends(obter_admin),
):
    """Cria novo papel customizado."""
    papel = gerenciador_papeis.criar_papel_customizado(nome, descricao, permissoes)

    if not papel:
        raise HTTPException(status_code=400, detail="Erro ao criar papel")

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        "papeis",
        "criar",
        True,
        {"papel": papel.codigo, "permissoes": len(permissoes)},
    )

    return {
        "sucesso": True,
        "mensagem": "Papel criado com sucesso",
        "papel": papel.to_dict(),
    }


@router.put(
    "/papeis/{codigo_papel}",
    summary="Atualizar papel",
)
async def atualizar_papel(
    codigo_papel: str,
    nome: Optional[str] = None,
    descricao: Optional[str] = None,
    permissoes: Optional[List[str]] = None,
    usuario_admin = Depends(obter_admin),
):
    """Atualiza papel."""
    if not gerenciador_papeis.atualizar_papel(
        codigo_papel,
        nome,
        descricao,
        permissoes,
    ):
        raise HTTPException(status_code=400, detail="Erro ao atualizar papel")

    papel = gerenciador_papeis.obter_papel(codigo_papel)

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"papel:{codigo_papel}",
        "atualizar",
        True,
    )

    return {
        "sucesso": True,
        "mensagem": "Papel atualizado com sucesso",
        "papel": papel.to_dict(),
    }


@router.post(
    "/papeis/{codigo_papel}/permissoes/{codigo_permissao}",
    summary="Adicionar permissão a papel",
)
async def adicionar_permissao_papel(
    codigo_papel: str,
    codigo_permissao: str,
    usuario_admin = Depends(obter_admin),
):
    """Adiciona permissão a um papel."""
    if not gerenciador_papeis.adicionar_permissao_papel(codigo_papel, codigo_permissao):
        raise HTTPException(status_code=400, detail="Erro ao adicionar permissão")

    papel = gerenciador_papeis.obter_papel(codigo_papel)

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"papel:{codigo_papel}",
        "adicionar_permissao",
        True,
        {"permissao": codigo_permissao},
    )

    return {
        "sucesso": True,
        "mensagem": "Permissão adicionada com sucesso",
        "papel": papel.to_dict(),
    }


@router.delete(
    "/papeis/{codigo_papel}/permissoes/{codigo_permissao}",
    summary="Remover permissão de papel",
)
async def remover_permissao_papel(
    codigo_papel: str,
    codigo_permissao: str,
    usuario_admin = Depends(obter_admin),
):
    """Remove permissão de um papel."""
    if not gerenciador_papeis.remover_permissao_papel(codigo_papel, codigo_permissao):
        raise HTTPException(status_code=400, detail="Erro ao remover permissão")

    papel = gerenciador_papeis.obter_papel(codigo_papel)

    # Registrar auditoria
    auditoria_acesso.registrar_acesso(
        usuario_admin.id,
        usuario_admin.email,
        f"papel:{codigo_papel}",
        "remover_permissao",
        True,
        {"permissao": codigo_permissao},
    )

    return {
        "sucesso": True,
        "mensagem": "Permissão removida com sucesso",
        "papel": papel.to_dict(),
    }


@router.get(
    "/permissoes",
    summary="Listar permissões",
)
async def listar_permissoes(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    usuario_admin = Depends(obter_admin),
):
    """Lista permissões do sistema."""
    if categoria:
        try:
            cat_enum = PermissaoCategoria(categoria)
            permissoes = gerenciador_papeis.listar_permissoes(cat_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Categoria inválida")
    else:
        permissoes = gerenciador_papeis.listar_permissoes()

    return {
        "total": len(permissoes),
        "permissoes": [p.to_dict() for p in permissoes],
    }


@router.get(
    "/permissoes/por-categoria",
    summary="Listar permissões por categoria",
)
async def listar_permissoes_por_categoria(
    usuario_admin = Depends(obter_admin),
):
    """Lista permissões agrupadas por categoria."""
    categorias = gerenciador_papeis.obter_permissoes_por_categoria()

    return {
        "total_categorias": len(categorias),
        "categorias": {
            cat: [p.to_dict() for p in perms]
            for cat, perms in categorias.items()
        },
    }


# ============================================================================
# Endpoints de Auditoria Avançada
# ============================================================================

@router.get(
    "/auditoria",
    summary="Obter registros de auditoria com filtros",
)
async def obter_auditoria_avancada(
    usuario_id: Optional[str] = Query(None, description="Filtrar por usuário"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    recurso: Optional[str] = Query(None, description="Filtrar por recurso"),
    sucesso: Optional[bool] = Query(None, description="Filtrar por sucesso"),
    limite: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    usuario_admin = Depends(obter_admin),
):
    """Obtém registros de auditoria com filtros avançados."""
    registros = auditoria_acesso.obter_registros(usuario_id, tipo, limite)

    # Aplicar filtros adicionais
    if recurso:
        registros = [r for r in registros if r.get("recurso") == recurso]

    if sucesso is not None:
        registros = [r for r in registros if r.get("sucesso") == sucesso]

    return {
        "total": len(registros),
        "registros": registros,
    }


@router.get(
    "/estatisticas",
    summary="Obter estatísticas do sistema",
)
async def obter_estatisticas_admin(
    usuario_admin = Depends(obter_admin),
):
    """Obtém estatísticas completas do sistema."""
    return {
        "usuarios": gerenciador_usuarios.obter_estatisticas(),
        "sessoes": gerenciador_sessao.obter_estatisticas(),
        "auditoria": auditoria_acesso.obter_estatisticas(),
        "papeis": gerenciador_papeis.obter_estatisticas(),
        "credito_autoral": "Criado por Eng. Anibal Nisgoski",
    }
