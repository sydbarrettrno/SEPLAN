"""
Gerenciador de Usuários
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa operações CRUD de usuários com validações e auditoria.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from api.auth.security import (
    GerenciadorSenha,
    Papel,
    gerenciador_senha,
)
from api.auth.models import UsuarioInterno


class GerenciadorUsuarios:
    """Gerenciador de usuários do sistema."""

    def __init__(self):
        """Inicializa gerenciador."""
        self.usuarios: Dict[str, UsuarioInterno] = {}
        self.usuarios_por_email: Dict[str, str] = {}

        # Criar usuário admin padrão
        self._criar_admin_padrao()

    def _criar_admin_padrao(self) -> None:
        """Cria usuário admin padrão se não existir."""
        email_admin = "admin@sistema-analitico.local"

        if email_admin not in self.usuarios_por_email:
            self.criar_usuario(
                nome="Administrador",
                email=email_admin,
                senha="AdminSeguro123!",
                papel=Papel.ADMIN,
                email_verificado=True,
            )

    def criar_usuario(
        self,
        nome: str,
        email: str,
        senha: str,
        papel: Papel = Papel.VISUALIZADOR,
        organizacao: Optional[str] = None,
        telefone: Optional[str] = None,
        email_verificado: bool = False,
    ) -> Optional[UsuarioInterno]:
        """
        Cria novo usuário.

        Args:
            nome: Nome do usuário
            email: Email único
            senha: Senha em texto plano
            papel: Papel do usuário
            organizacao: Organização
            telefone: Telefone
            email_verificado: Se email já está verificado

        Returns:
            UsuarioInterno criado ou None se email duplicado
        """
        # Validar email duplicado
        if email.lower() in self.usuarios_por_email:
            return None

        # Gerar ID e hash de senha
        usuario_id = f"usr_{uuid.uuid4().hex[:12]}"
        hash_senha, salt = gerenciador_senha.hash_senha(senha)

        # Criar usuário
        usuario = UsuarioInterno(
            id=usuario_id,
            nome=nome,
            email=email.lower(),
            papel=papel,
            hash_senha=hash_senha,
            salt_senha=salt,
            organizacao=organizacao,
            telefone=telefone,
            ativo=True,
            email_verificado=email_verificado,
            criado_em=datetime.utcnow(),
            atualizado_em=datetime.utcnow(),
        )

        # Armazenar
        self.usuarios[usuario_id] = usuario
        self.usuarios_por_email[email.lower()] = usuario_id

        return usuario

    def obter_usuario_por_id(self, usuario_id: str) -> Optional[UsuarioInterno]:
        """Obtém usuário por ID."""
        return self.usuarios.get(usuario_id)

    def obter_usuario_por_email(self, email: str) -> Optional[UsuarioInterno]:
        """Obtém usuário por email."""
        usuario_id = self.usuarios_por_email.get(email.lower())
        if usuario_id:
            return self.usuarios.get(usuario_id)
        return None

    def autenticar_usuario(
        self,
        email: str,
        senha: str,
    ) -> Optional[UsuarioInterno]:
        """
        Autentica usuário com email e senha.

        Args:
            email: Email do usuário
            senha: Senha em texto plano

        Returns:
            UsuarioInterno se autenticado, None caso contrário
        """
        usuario = self.obter_usuario_por_email(email)

        if not usuario:
            return None

        # Verificar se está ativo
        if not usuario.ativo:
            return None

        # Verificar se está bloqueado
        if usuario.bloqueado_ate:
            if datetime.utcnow() < usuario.bloqueado_ate:
                return None
            else:
                # Desbloquear
                usuario.bloqueado_ate = None
                usuario.tentativas_login_falha = 0

        # Verificar senha
        if not gerenciador_senha.verificar_senha(
            senha,
            usuario.hash_senha,
            usuario.salt_senha,
        ):
            # Incrementar tentativas falhas
            usuario.tentativas_login_falha += 1

            # Bloquear após 5 tentativas
            if usuario.tentativas_login_falha >= 5:
                usuario.bloqueado_ate = datetime.utcnow() + timedelta(minutes=15)

            return None

        # Reset tentativas falhas
        usuario.tentativas_login_falha = 0
        usuario.ultimo_login = datetime.utcnow()

        return usuario

    def atualizar_usuario(
        self,
        usuario_id: str,
        **kwargs,
    ) -> Optional[UsuarioInterno]:
        """
        Atualiza dados do usuário.

        Args:
            usuario_id: ID do usuário
            **kwargs: Campos a atualizar

        Returns:
            UsuarioInterno atualizado ou None
        """
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return None

        # Campos permitidos
        campos_permitidos = {
            "nome",
            "organizacao",
            "telefone",
            "foto_perfil_url",
            "ativo",
            "email_verificado",
        }

        # Atualizar campos
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                setattr(usuario, campo, valor)

        usuario.atualizado_em = datetime.utcnow()

        return usuario

    def alterar_senha(
        self,
        usuario_id: str,
        senha_atual: str,
        senha_nova: str,
    ) -> bool:
        """
        Altera senha do usuário.

        Args:
            usuario_id: ID do usuário
            senha_atual: Senha atual
            senha_nova: Nova senha

        Returns:
            True se alterada com sucesso, False caso contrário
        """
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        # Verificar senha atual
        if not gerenciador_senha.verificar_senha(
            senha_atual,
            usuario.hash_senha,
            usuario.salt_senha,
        ):
            return False

        # Gerar novo hash
        novo_hash, novo_salt = gerenciador_senha.hash_senha(senha_nova)

        usuario.hash_senha = novo_hash
        usuario.salt_senha = novo_salt
        usuario.atualizado_em = datetime.utcnow()

        return True

    def resetar_senha(self, usuario_id: str, nova_senha: str) -> bool:
        """
        Reseta senha do usuário (admin).

        Args:
            usuario_id: ID do usuário
            nova_senha: Nova senha

        Returns:
            True se resetada com sucesso
        """
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        novo_hash, novo_salt = gerenciador_senha.hash_senha(nova_senha)

        usuario.hash_senha = novo_hash
        usuario.salt_senha = novo_salt
        usuario.tentativas_login_falha = 0
        usuario.bloqueado_ate = None
        usuario.atualizado_em = datetime.utcnow()

        return True

    def desativar_usuario(self, usuario_id: str) -> bool:
        """Desativa usuário."""
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        usuario.ativo = False
        usuario.atualizado_em = datetime.utcnow()

        return True

    def ativar_usuario(self, usuario_id: str) -> bool:
        """Ativa usuário."""
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        usuario.ativo = True
        usuario.atualizado_em = datetime.utcnow()

        return True

    def alterar_papel(self, usuario_id: str, novo_papel: Papel) -> bool:
        """Altera papel do usuário."""
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        usuario.papel = novo_papel
        usuario.atualizado_em = datetime.utcnow()

        return True

    def verificar_email(self, usuario_id: str) -> bool:
        """Marca email como verificado."""
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        usuario.email_verificado = True
        usuario.atualizado_em = datetime.utcnow()

        return True

    def listar_usuarios(
        self,
        papel: Optional[Papel] = None,
        ativo: Optional[bool] = None,
        limite: int = 100,
    ) -> List[UsuarioInterno]:
        """
        Lista usuários com filtros.

        Args:
            papel: Filtrar por papel
            ativo: Filtrar por status ativo
            limite: Limite de resultados

        Returns:
            Lista de usuários
        """
        usuarios = list(self.usuarios.values())

        if papel:
            usuarios = [u for u in usuarios if u.papel == papel]

        if ativo is not None:
            usuarios = [u for u in usuarios if u.ativo == ativo]

        return usuarios[:limite]

    def contar_usuarios(self, papel: Optional[Papel] = None) -> int:
        """Conta total de usuários."""
        usuarios = list(self.usuarios.values())

        if papel:
            usuarios = [u for u in usuarios if u.papel == papel]

        return len(usuarios)

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas de usuários."""
        usuarios = list(self.usuarios.values())

        return {
            "total_usuarios": len(usuarios),
            "usuarios_ativos": len([u for u in usuarios if u.ativo]),
            "usuarios_inativos": len([u for u in usuarios if not u.ativo]),
            "por_papel": {
                papel.value: len([u for u in usuarios if u.papel == papel])
                for papel in Papel
            },
            "emails_verificados": len([u for u in usuarios if u.email_verificado]),
            "bloqueados": len([u for u in usuarios if u.bloqueado_ate]),
        }

    def deletar_usuario(self, usuario_id: str) -> bool:
        """Deleta usuário (irreversível)."""
        usuario = self.obter_usuario_por_id(usuario_id)

        if not usuario:
            return False

        # Remover dos índices
        del self.usuarios[usuario_id]
        del self.usuarios_por_email[usuario.email]

        return True


# Instância global
gerenciador_usuarios = GerenciadorUsuarios()
