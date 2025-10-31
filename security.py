"""
Módulo de Segurança e Autenticação
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa autenticação JWT, OAuth2 e controle de acesso baseado em papéis.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import jwt
import hashlib
import secrets
from functools import wraps

from api.config import config


class Papel(str, Enum):
    """Papéis de usuário no sistema."""
    ADMIN = "admin"
    ANALISTA = "analista"
    VISUALIZADOR = "visualizador"
    CONVIDADO = "convidado"


class TipoToken(str, Enum):
    """Tipos de token."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_SENHA = "reset_senha"


class GerenciadorSenha:
    """Gerenciador de senhas com hash seguro."""

    @staticmethod
    def hash_senha(senha: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Gera hash seguro de senha com salt.

        Args:
            senha: Senha em texto plano
            salt: Salt (gerado se não fornecido)

        Returns:
            Tupla (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)

        # PBKDF2 com SHA256
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            senha.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterações
        )

        hash_hex = hash_obj.hex()
        return hash_hex, salt

    @staticmethod
    def verificar_senha(senha: str, hash_armazenado: str, salt: str) -> bool:
        """
        Verifica se senha corresponde ao hash.

        Args:
            senha: Senha em texto plano
            hash_armazenado: Hash armazenado
            salt: Salt usado

        Returns:
            True se corresponde, False caso contrário
        """
        hash_novo, _ = GerenciadorSenha.hash_senha(senha, salt)
        return hash_novo == hash_armazenado

    @staticmethod
    def gerar_senha_temporaria(tamanho: int = 12) -> str:
        """Gera senha temporária aleatória."""
        return secrets.token_urlsafe(tamanho)


class GerenciadorJWT:
    """Gerenciador de tokens JWT."""

    @staticmethod
    def criar_token(
        dados: Dict[str, Any],
        tipo_token: TipoToken = TipoToken.ACCESS,
        expiracao_minutos: Optional[int] = None,
    ) -> str:
        """
        Cria token JWT.

        Args:
            dados: Dados a codificar
            tipo_token: Tipo de token
            expiracao_minutos: Minutos até expiração

        Returns:
            Token JWT
        """
        if expiracao_minutos is None:
            if tipo_token == TipoToken.ACCESS:
                expiracao_minutos = config.ACCESS_TOKEN_EXPIRE_MINUTES
            elif tipo_token == TipoToken.REFRESH:
                expiracao_minutos = 7 * 24 * 60  # 7 dias
            else:
                expiracao_minutos = 24 * 60  # 24 horas

        # Copiar dados e adicionar metadata
        payload = dados.copy()
        payload["tipo"] = tipo_token.value
        payload["iat"] = datetime.utcnow()
        payload["exp"] = datetime.utcnow() + timedelta(minutes=expiracao_minutos)

        # Codificar token
        token = jwt.encode(
            payload,
            config.SECRET_KEY,
            algorithm=config.ALGORITHM,
        )

        return token

    @staticmethod
    def verificar_token(token: str, tipo_esperado: TipoToken = TipoToken.ACCESS) -> Optional[Dict[str, Any]]:
        """
        Verifica e decodifica token JWT.

        Args:
            token: Token a verificar
            tipo_esperado: Tipo de token esperado

        Returns:
            Dados decodificados ou None se inválido
        """
        try:
            payload = jwt.decode(
                token,
                config.SECRET_KEY,
                algorithms=[config.ALGORITHM],
            )

            # Verificar tipo
            if payload.get("tipo") != tipo_esperado.value:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def renovar_token(refresh_token: str) -> Optional[str]:
        """
        Renova access token usando refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Novo access token ou None se inválido
        """
        payload = GerenciadorJWT.verificar_token(
            refresh_token, TipoToken.REFRESH
        )

        if not payload:
            return None

        # Remover campos de expiração
        payload.pop("exp", None)
        payload.pop("iat", None)
        payload.pop("tipo", None)

        # Criar novo access token
        return GerenciadorJWT.criar_token(
            payload,
            TipoToken.ACCESS,
        )


class ControladorAcesso:
    """Controlador de acesso baseado em papéis (RBAC)."""

    # Permissões por papel
    PERMISSOES = {
        Papel.ADMIN: [
            "analisar",
            "gerenciar_usuarios",
            "gerenciar_documentos",
            "gerenciar_configuracoes",
            "visualizar_auditoria",
            "exportar_dados",
        ],
        Papel.ANALISTA: [
            "analisar",
            "gerenciar_documentos",
            "visualizar_resultados",
            "exportar_dados",
        ],
        Papel.VISUALIZADOR: [
            "visualizar_resultados",
            "exportar_dados",
        ],
        Papel.CONVIDADO: [
            "visualizar_resultados",
        ],
    }

    @staticmethod
    def verificar_permissao(
        papel: Papel,
        permissao_necessaria: str,
    ) -> bool:
        """
        Verifica se papel tem permissão.

        Args:
            papel: Papel do usuário
            permissao_necessaria: Permissão necessária

        Returns:
            True se tem permissão, False caso contrário
        """
        permissoes = ControladorAcesso.PERMISSOES.get(papel, [])
        return permissao_necessaria in permissoes

    @staticmethod
    def obter_permissoes(papel: Papel) -> list[str]:
        """Obtém lista de permissões de um papel."""
        return ControladorAcesso.PERMISSOES.get(papel, [])

    @staticmethod
    def adicionar_permissao(papel: Papel, permissao: str) -> None:
        """Adiciona permissão a um papel."""
        if papel not in ControladorAcesso.PERMISSOES:
            ControladorAcesso.PERMISSOES[papel] = []

        if permissao not in ControladorAcesso.PERMISSOES[papel]:
            ControladorAcesso.PERMISSOES[papel].append(permissao)

    @staticmethod
    def remover_permissao(papel: Papel, permissao: str) -> None:
        """Remove permissão de um papel."""
        if papel in ControladorAcesso.PERMISSOES:
            if permissao in ControladorAcesso.PERMISSOES[papel]:
                ControladorAcesso.PERMISSOES[papel].remove(permissao)


class GerenciadorSessao:
    """Gerenciador de sessões de usuário."""

    def __init__(self):
        """Inicializa gerenciador."""
        self.sessoes: Dict[str, Dict[str, Any]] = {}

    def criar_sessao(
        self,
        usuario_id: str,
        usuario_email: str,
        papel: Papel,
        ip_address: str,
        user_agent: str,
    ) -> str:
        """
        Cria nova sessão.

        Args:
            usuario_id: ID do usuário
            usuario_email: Email do usuário
            papel: Papel do usuário
            ip_address: Endereço IP
            user_agent: User agent do navegador

        Returns:
            ID da sessão
        """
        sessao_id = secrets.token_urlsafe(32)

        self.sessoes[sessao_id] = {
            "usuario_id": usuario_id,
            "usuario_email": usuario_email,
            "papel": papel.value,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "criada_em": datetime.utcnow(),
            "ultima_atividade": datetime.utcnow(),
            "ativa": True,
        }

        return sessao_id

    def obter_sessao(self, sessao_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de sessão."""
        sessao = self.sessoes.get(sessao_id)

        if not sessao or not sessao.get("ativa"):
            return None

        # Verificar expiração (24 horas de inatividade)
        ultima_atividade = sessao.get("ultima_atividade")
        if ultima_atividade:
            tempo_inativo = datetime.utcnow() - ultima_atividade
            if tempo_inativo > timedelta(hours=24):
                self.encerrar_sessao(sessao_id)
                return None

        # Atualizar última atividade
        sessao["ultima_atividade"] = datetime.utcnow()
        return sessao

    def encerrar_sessao(self, sessao_id: str) -> bool:
        """Encerra uma sessão."""
        if sessao_id in self.sessoes:
            self.sessoes[sessao_id]["ativa"] = False
            return True
        return False

    def encerrar_todas_sessoes(self, usuario_id: str) -> int:
        """Encerra todas as sessões de um usuário."""
        count = 0
        for sessao_id, sessao in self.sessoes.items():
            if sessao.get("usuario_id") == usuario_id:
                self.encerrar_sessao(sessao_id)
                count += 1
        return count

    def obter_sessoes_usuario(self, usuario_id: str) -> list[Dict[str, Any]]:
        """Obtém todas as sessões ativas de um usuário."""
        return [
            sessao for sessao in self.sessoes.values()
            if sessao.get("usuario_id") == usuario_id and sessao.get("ativa")
        ]

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas de sessões."""
        sessoes_ativas = [s for s in self.sessoes.values() if s.get("ativa")]
        return {
            "total_sessoes": len(self.sessoes),
            "sessoes_ativas": len(sessoes_ativas),
            "sessoes_encerradas": len(self.sessoes) - len(sessoes_ativas),
        }


class AuditoriaAcesso:
    """Auditor de acessos ao sistema."""

    def __init__(self):
        """Inicializa auditor."""
        self.registros: list[Dict[str, Any]] = []

    def registrar_login(
        self,
        usuario_id: str,
        usuario_email: str,
        ip_address: str,
        sucesso: bool,
        motivo_falha: Optional[str] = None,
    ) -> None:
        """Registra tentativa de login."""
        self.registros.append({
            "tipo": "login",
            "usuario_id": usuario_id,
            "usuario_email": usuario_email,
            "ip_address": ip_address,
            "sucesso": sucesso,
            "motivo_falha": motivo_falha,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def registrar_logout(
        self,
        usuario_id: str,
        usuario_email: str,
        ip_address: str,
    ) -> None:
        """Registra logout."""
        self.registros.append({
            "tipo": "logout",
            "usuario_id": usuario_id,
            "usuario_email": usuario_email,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def registrar_acesso(
        self,
        usuario_id: str,
        usuario_email: str,
        recurso: str,
        acao: str,
        sucesso: bool,
        detalhes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra acesso a recurso."""
        self.registros.append({
            "tipo": "acesso",
            "usuario_id": usuario_id,
            "usuario_email": usuario_email,
            "recurso": recurso,
            "acao": acao,
            "sucesso": sucesso,
            "detalhes": detalhes,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def registrar_erro_autenticacao(
        self,
        usuario_email: str,
        ip_address: str,
        motivo: str,
    ) -> None:
        """Registra erro de autenticação."""
        self.registros.append({
            "tipo": "erro_autenticacao",
            "usuario_email": usuario_email,
            "ip_address": ip_address,
            "motivo": motivo,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def obter_registros(
        self,
        usuario_id: Optional[str] = None,
        tipo: Optional[str] = None,
        limite: int = 100,
    ) -> list[Dict[str, Any]]:
        """Obtém registros de auditoria."""
        registros = self.registros

        if usuario_id:
            registros = [r for r in registros if r.get("usuario_id") == usuario_id]

        if tipo:
            registros = [r for r in registros if r.get("tipo") == tipo]

        return registros[-limite:]

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas de auditoria."""
        logins_sucesso = len([r for r in self.registros if r.get("tipo") == "login" and r.get("sucesso")])
        logins_falha = len([r for r in self.registros if r.get("tipo") == "login" and not r.get("sucesso")])
        logouts = len([r for r in self.registros if r.get("tipo") == "logout"])

        return {
            "total_registros": len(self.registros),
            "logins_sucesso": logins_sucesso,
            "logins_falha": logins_falha,
            "logouts": logouts,
            "erros_autenticacao": len([r for r in self.registros if r.get("tipo") == "erro_autenticacao"]),
        }


# Instâncias globais
gerenciador_senha = GerenciadorSenha()
gerenciador_jwt = GerenciadorJWT()
controlador_acesso = ControladorAcesso()
gerenciador_sessao = GerenciadorSessao()
auditoria_acesso = AuditoriaAcesso()
