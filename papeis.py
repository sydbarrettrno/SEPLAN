"""
Gerenciador de Papéis e Permissões
Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski

Implementa gerenciamento dinâmico de papéis e permissões customizáveis.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import uuid


class PermissaoCategoria(str, Enum):
    """Categorias de permissões."""
    ANALISE = "analise"
    DOCUMENTOS = "documentos"
    USUARIOS = "usuarios"
    CONFIGURACOES = "configuracoes"
    AUDITORIA = "auditoria"
    RELATORIOS = "relatorios"
    INTEGRACAO = "integracao"


class Permissao:
    """Representa uma permissão no sistema."""

    def __init__(
        self,
        codigo: str,
        nome: str,
        descricao: str,
        categoria: PermissaoCategoria,
        requer_permissoes: Optional[List[str]] = None,
    ):
        """
        Inicializa permissão.

        Args:
            codigo: Código único da permissão
            nome: Nome legível
            descricao: Descrição da permissão
            categoria: Categoria
            requer_permissoes: Permissões que esta depende
        """
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.categoria = categoria
        self.requer_permissoes = requer_permissoes or []

    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "categoria": self.categoria.value,
            "requer_permissoes": self.requer_permissoes,
        }


class Papel:
    """Representa um papel no sistema."""

    def __init__(
        self,
        codigo: str,
        nome: str,
        descricao: str,
        permissoes: Optional[List[str]] = None,
        ativo: bool = True,
        criado_em: Optional[datetime] = None,
    ):
        """
        Inicializa papel.

        Args:
            codigo: Código único do papel
            nome: Nome legível
            descricao: Descrição
            permissoes: Lista de códigos de permissões
            ativo: Se está ativo
            criado_em: Data de criação
        """
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.permissoes: Set[str] = set(permissoes or [])
        self.ativo = ativo
        self.criado_em = criado_em or datetime.utcnow()
        self.atualizado_em = datetime.utcnow()
        self.customizado = False  # Se foi customizado pelo admin

    def adicionar_permissao(self, codigo_permissao: str) -> bool:
        """Adiciona permissão ao papel."""
        if codigo_permissao not in self.permissoes:
            self.permissoes.add(codigo_permissao)
            self.atualizado_em = datetime.utcnow()
            return True
        return False

    def remover_permissao(self, codigo_permissao: str) -> bool:
        """Remove permissão do papel."""
        if codigo_permissao in self.permissoes:
            self.permissoes.discard(codigo_permissao)
            self.atualizado_em = datetime.utcnow()
            return True
        return False

    def tem_permissao(self, codigo_permissao: str) -> bool:
        """Verifica se tem permissão."""
        return codigo_permissao in self.permissoes

    def obter_permissoes(self) -> List[str]:
        """Retorna lista de permissões."""
        return sorted(list(self.permissoes))

    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "descricao": self.descricao,
            "permissoes": self.obter_permissoes(),
            "total_permissoes": len(self.permissoes),
            "ativo": self.ativo,
            "customizado": self.customizado,
            "criado_em": self.criado_em.isoformat(),
            "atualizado_em": self.atualizado_em.isoformat(),
        }


class GerenciadorPapeis:
    """Gerenciador de papéis e permissões do sistema."""

    def __init__(self):
        """Inicializa gerenciador."""
        self.papeis: Dict[str, Papel] = {}
        self.permissoes: Dict[str, Permissao] = {}

        # Inicializar permissões padrão
        self._inicializar_permissoes_padrao()

        # Inicializar papéis padrão
        self._inicializar_papeis_padrao()

    def _inicializar_permissoes_padrao(self) -> None:
        """Cria permissões padrão do sistema."""
        permissoes_padrao = [
            # Análise
            Permissao(
                "analisar:criar",
                "Criar Análise",
                "Pode criar novas análises",
                PermissaoCategoria.ANALISE,
            ),
            Permissao(
                "analisar:visualizar",
                "Visualizar Análise",
                "Pode visualizar análises",
                PermissaoCategoria.ANALISE,
            ),
            Permissao(
                "analisar:editar",
                "Editar Análise",
                "Pode editar análises",
                PermissaoCategoria.ANALISE,
                ["analisar:visualizar"],
            ),
            Permissao(
                "analisar:deletar",
                "Deletar Análise",
                "Pode deletar análises",
                PermissaoCategoria.ANALISE,
                ["analisar:editar"],
            ),

            # Documentos
            Permissao(
                "documentos:ingerir",
                "Ingerir Documentos",
                "Pode ingerir documentos no RAG",
                PermissaoCategoria.DOCUMENTOS,
            ),
            Permissao(
                "documentos:listar",
                "Listar Documentos",
                "Pode listar documentos",
                PermissaoCategoria.DOCUMENTOS,
            ),
            Permissao(
                "documentos:deletar",
                "Deletar Documentos",
                "Pode deletar documentos",
                PermissaoCategoria.DOCUMENTOS,
                ["documentos:listar"],
            ),

            # Usuários
            Permissao(
                "usuarios:listar",
                "Listar Usuários",
                "Pode listar usuários",
                PermissaoCategoria.USUARIOS,
            ),
            Permissao(
                "usuarios:criar",
                "Criar Usuário",
                "Pode criar novos usuários",
                PermissaoCategoria.USUARIOS,
            ),
            Permissao(
                "usuarios:editar",
                "Editar Usuário",
                "Pode editar dados de usuários",
                PermissaoCategoria.USUARIOS,
                ["usuarios:listar"],
            ),
            Permissao(
                "usuarios:deletar",
                "Deletar Usuário",
                "Pode deletar usuários",
                PermissaoCategoria.USUARIOS,
                ["usuarios:editar"],
            ),
            Permissao(
                "usuarios:alterar_papel",
                "Alterar Papel",
                "Pode alterar papel de usuários",
                PermissaoCategoria.USUARIOS,
                ["usuarios:editar"],
            ),
            Permissao(
                "usuarios:resetar_senha",
                "Resetar Senha",
                "Pode resetar senha de usuários",
                PermissaoCategoria.USUARIOS,
                ["usuarios:editar"],
            ),

            # Configurações
            Permissao(
                "configuracoes:visualizar",
                "Visualizar Configurações",
                "Pode visualizar configurações",
                PermissaoCategoria.CONFIGURACOES,
            ),
            Permissao(
                "configuracoes:editar",
                "Editar Configurações",
                "Pode editar configurações",
                PermissaoCategoria.CONFIGURACOES,
                ["configuracoes:visualizar"],
            ),

            # Auditoria
            Permissao(
                "auditoria:visualizar",
                "Visualizar Auditoria",
                "Pode visualizar registros de auditoria",
                PermissaoCategoria.AUDITORIA,
            ),
            Permissao(
                "auditoria:exportar",
                "Exportar Auditoria",
                "Pode exportar registros de auditoria",
                PermissaoCategoria.AUDITORIA,
                ["auditoria:visualizar"],
            ),

            # Relatórios
            Permissao(
                "relatorios:gerar",
                "Gerar Relatórios",
                "Pode gerar relatórios",
                PermissaoCategoria.RELATORIOS,
            ),
            Permissao(
                "relatorios:exportar",
                "Exportar Relatórios",
                "Pode exportar relatórios",
                PermissaoCategoria.RELATORIOS,
                ["relatorios:gerar"],
            ),

            # Integração
            Permissao(
                "integracao:n8n",
                "Integração n8n",
                "Pode gerenciar workflows n8n",
                PermissaoCategoria.INTEGRACAO,
            ),
        ]

        for permissao in permissoes_padrao:
            self.permissoes[permissao.codigo] = permissao

    def _inicializar_papeis_padrao(self) -> None:
        """Cria papéis padrão do sistema."""
        # Admin - todas as permissões
        papel_admin = Papel(
            "admin",
            "Administrador",
            "Acesso total ao sistema",
            list(self.permissoes.keys()),
        )
        self.papeis["admin"] = papel_admin

        # Analista - permissões de análise e documentos
        papel_analista = Papel(
            "analista",
            "Analista",
            "Pode realizar análises e gerenciar documentos",
            [
                "analisar:criar",
                "analisar:visualizar",
                "analisar:editar",
                "documentos:ingerir",
                "documentos:listar",
                "relatorios:gerar",
                "relatorios:exportar",
            ],
        )
        self.papeis["analista"] = papel_analista

        # Visualizador - apenas visualização
        papel_visualizador = Papel(
            "visualizador",
            "Visualizador",
            "Pode visualizar análises e relatórios",
            [
                "analisar:visualizar",
                "documentos:listar",
                "relatorios:gerar",
            ],
        )
        self.papeis["visualizador"] = papel_visualizador

        # Convidado - visualização limitada
        papel_convidado = Papel(
            "convidado",
            "Convidado",
            "Acesso limitado para visualização",
            [
                "analisar:visualizar",
            ],
        )
        self.papeis["convidado"] = papel_convidado

    def criar_papel_customizado(
        self,
        nome: str,
        descricao: str,
        permissoes: List[str],
    ) -> Optional[Papel]:
        """
        Cria novo papel customizado.

        Args:
            nome: Nome do papel
            descricao: Descrição
            permissoes: Lista de códigos de permissões

        Returns:
            Papel criado ou None se erro
        """
        # Validar permissões
        for codigo in permissoes:
            if codigo not in self.permissoes:
                return None

        # Gerar código único
        codigo = f"custom_{uuid.uuid4().hex[:8]}"

        papel = Papel(codigo, nome, descricao, permissoes)
        papel.customizado = True

        self.papeis[codigo] = papel
        return papel

    def obter_papel(self, codigo: str) -> Optional[Papel]:
        """Obtém papel por código."""
        return self.papeis.get(codigo)

    def listar_papeis(self, apenas_ativos: bool = True) -> List[Papel]:
        """Lista papéis."""
        papeis = list(self.papeis.values())

        if apenas_ativos:
            papeis = [p for p in papeis if p.ativo]

        return sorted(papeis, key=lambda p: p.nome)

    def atualizar_papel(
        self,
        codigo: str,
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
        permissoes: Optional[List[str]] = None,
    ) -> bool:
        """Atualiza papel."""
        papel = self.obter_papel(codigo)

        if not papel:
            return False

        if nome:
            papel.nome = nome

        if descricao:
            papel.descricao = descricao

        if permissoes is not None:
            # Validar permissões
            for codigo_perm in permissoes:
                if codigo_perm not in self.permissoes:
                    return False

            papel.permissoes = set(permissoes)

        papel.atualizado_em = datetime.utcnow()
        return True

    def adicionar_permissao_papel(self, codigo_papel: str, codigo_permissao: str) -> bool:
        """Adiciona permissão a um papel."""
        papel = self.obter_papel(codigo_papel)

        if not papel or codigo_permissao not in self.permissoes:
            return False

        return papel.adicionar_permissao(codigo_permissao)

    def remover_permissao_papel(self, codigo_papel: str, codigo_permissao: str) -> bool:
        """Remove permissão de um papel."""
        papel = self.obter_papel(codigo_papel)

        if not papel:
            return False

        return papel.remover_permissao(codigo_permissao)

    def desativar_papel(self, codigo: str) -> bool:
        """Desativa papel."""
        papel = self.obter_papel(codigo)

        if not papel or codigo in ["admin", "analista", "visualizador", "convidado"]:
            # Não permitir desativar papéis padrão
            return False

        papel.ativo = False
        papel.atualizado_em = datetime.utcnow()
        return True

    def ativar_papel(self, codigo: str) -> bool:
        """Ativa papel."""
        papel = self.obter_papel(codigo)

        if not papel:
            return False

        papel.ativo = True
        papel.atualizado_em = datetime.utcnow()
        return True

    def deletar_papel(self, codigo: str) -> bool:
        """Deleta papel customizado."""
        papel = self.obter_papel(codigo)

        if not papel or not papel.customizado:
            # Não permitir deletar papéis padrão
            return False

        del self.papeis[codigo]
        return True

    def obter_permissao(self, codigo: str) -> Optional[Permissao]:
        """Obtém permissão por código."""
        return self.permissoes.get(codigo)

    def listar_permissoes(
        self,
        categoria: Optional[PermissaoCategoria] = None,
    ) -> List[Permissao]:
        """Lista permissões."""
        permissoes = list(self.permissoes.values())

        if categoria:
            permissoes = [p for p in permissoes if p.categoria == categoria]

        return sorted(permissoes, key=lambda p: p.nome)

    def obter_permissoes_por_categoria(self) -> Dict[str, List[Permissao]]:
        """Agrupa permissões por categoria."""
        resultado = {}

        for categoria in PermissaoCategoria:
            resultado[categoria.value] = self.listar_permissoes(categoria)

        return resultado

    def verificar_permissao_papel(self, codigo_papel: str, codigo_permissao: str) -> bool:
        """Verifica se papel tem permissão."""
        papel = self.obter_papel(codigo_papel)

        if not papel:
            return False

        return papel.tem_permissao(codigo_permissao)

    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas."""
        papeis = list(self.papeis.values())

        return {
            "total_papeis": len(papeis),
            "papeis_ativos": len([p for p in papeis if p.ativo]),
            "papeis_customizados": len([p for p in papeis if p.customizado]),
            "total_permissoes": len(self.permissoes),
            "permissoes_por_categoria": {
                cat.value: len(self.listar_permissoes(cat))
                for cat in PermissaoCategoria
            },
        }


# Instância global
gerenciador_papeis = GerenciadorPapeis()
