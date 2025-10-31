import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { AlertCircle, Users, Lock, Settings, Shield, Trash2, Edit2, Search, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth } from '@/_core/hooks/useAuth';
import { toast } from 'sonner';

interface Usuario {
  id: string;
  nome: string;
  email: string;
  papel: string;
  organizacao?: string;
  ativo: boolean;
  email_verificado: boolean;
  criado_em: string;
  ultimo_login?: string;
}

interface Papel {
  codigo: string;
  nome: string;
  descricao: string;
  permissoes: string[];
  total_permissoes: number;
  ativo: boolean;
  customizado: boolean;
}

interface Permissao {
  codigo: string;
  nome: string;
  descricao: string;
  categoria: string;
}

export default function AdminPanel() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('usuarios');
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [papeis, setPapeis] = useState<Papel[]>([]);
  const [permissoes, setPermissoes] = useState<Permissao[]>([]);
  const [loading, setLoading] = useState(false);
  const [busca, setBusca] = useState('');
  const [paginaAtual, setPaginaAtual] = useState(1);

  // Verificar se é admin
  if (user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              Acesso Negado
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Você não tem permissão para acessar o painel de administração.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Carregar dados
  useEffect(() => {
    carregarUsuarios();
    carregarPapeis();
    carregarPermissoes();
  }, [paginaAtual]);

  const carregarUsuarios = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/admin/usuarios?pagina=${paginaAtual}&limite=20&busca=${busca}`);
      const data = await response.json();
      setUsuarios(data.usuarios || []);
    } catch (error) {
      toast.error('Erro ao carregar usuários');
    } finally {
      setLoading(false);
    }
  };

  const carregarPapeis = async () => {
    try {
      const response = await fetch('/api/admin/papeis');
      const data = await response.json();
      setPapeis(data.papeis || []);
    } catch (error) {
      toast.error('Erro ao carregar papéis');
    }
  };

  const carregarPermissoes = async () => {
    try {
      const response = await fetch('/api/admin/permissoes');
      const data = await response.json();
      setPermissoes(data.permissoes || []);
    } catch (error) {
      toast.error('Erro ao carregar permissões');
    }
  };

  const handleAlterarPapel = async (usuarioId: string, novoPapel: string) => {
    try {
      const response = await fetch(`/api/auth/usuarios/${usuarioId}/papel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ novo_papel: novoPapel }),
      });

      if (response.ok) {
        toast.success('Papel alterado com sucesso');
        carregarUsuarios();
      } else {
        toast.error('Erro ao alterar papel');
      }
    } catch (error) {
      toast.error('Erro ao alterar papel');
    }
  };

  const handleDesativarUsuario = async (usuarioId: string) => {
    if (!confirm('Tem certeza que deseja desativar este usuário?')) return;

    try {
      const response = await fetch(`/api/auth/usuarios/${usuarioId}/desativar`, {
        method: 'POST',
      });

      if (response.ok) {
        toast.success('Usuário desativado com sucesso');
        carregarUsuarios();
      } else {
        toast.error('Erro ao desativar usuário');
      }
    } catch (error) {
      toast.error('Erro ao desativar usuário');
    }
  };

  const handleResetarSenha = async (usuarioId: string) => {
    try {
      const response = await fetch(`/api/admin/usuarios/${usuarioId}/resetar-senha`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(`Senha temporária: ${data.senha_temporaria}`);
      } else {
        toast.error('Erro ao resetar senha');
      }
    } catch (error) {
      toast.error('Erro ao resetar senha');
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Shield className="w-8 h-8" />
              Painel de Administração
            </h1>
            <p className="text-sm text-muted-foreground">
              Criado por Eng. Anibal Nisgoski
            </p>
          </div>
          <p className="text-muted-foreground">
            Gerencie usuários, papéis e permissões do sistema
          </p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="usuarios" className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Usuários
            </TabsTrigger>
            <TabsTrigger value="papeis" className="flex items-center gap-2">
              <Lock className="w-4 h-4" />
              Papéis
            </TabsTrigger>
            <TabsTrigger value="permissoes" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Permissões
            </TabsTrigger>
          </TabsList>

          {/* Tab: Usuários */}
          <TabsContent value="usuarios" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Gerenciar Usuários</CardTitle>
                <CardDescription>
                  Visualize, edite e gerencie todos os usuários do sistema
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Barra de Busca */}
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Buscar por nome ou email..."
                      value={busca}
                      onChange={(e) => {
                        setBusca(e.target.value);
                        setPaginaAtual(1);
                      }}
                      className="pl-10"
                    />
                  </div>
                  <Button onClick={() => carregarUsuarios()}>
                    Buscar
                  </Button>
                </div>

                {/* Tabela de Usuários */}
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Nome</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Papel</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Último Login</TableHead>
                        <TableHead className="text-right">Ações</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {usuarios.map((usuario) => (
                        <TableRow key={usuario.id}>
                          <TableCell className="font-medium">{usuario.nome}</TableCell>
                          <TableCell className="text-sm">{usuario.email}</TableCell>
                          <TableCell>
                            <Select value={usuario.papel} onValueChange={(valor) => handleAlterarPapel(usuario.id, valor)}>
                              <SelectTrigger className="w-32">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="admin">Admin</SelectItem>
                                <SelectItem value="analista">Analista</SelectItem>
                                <SelectItem value="visualizador">Visualizador</SelectItem>
                                <SelectItem value="convidado">Convidado</SelectItem>
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Badge variant={usuario.ativo ? 'default' : 'secondary'}>
                              {usuario.ativo ? 'Ativo' : 'Inativo'}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {usuario.ultimo_login ? new Date(usuario.ultimo_login).toLocaleDateString() : 'Nunca'}
                          </TableCell>
                          <TableCell className="text-right space-x-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleResetarSenha(usuario.id)}
                            >
                              <Lock className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDesativarUsuario(usuario.id)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Paginação */}
                <div className="flex items-center justify-between">
                  <p className="text-sm text-muted-foreground">
                    Total de usuários: {usuarios.length}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPaginaAtual(Math.max(1, paginaAtual - 1))}
                      disabled={paginaAtual === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <span className="px-3 py-2 text-sm">Página {paginaAtual}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPaginaAtual(paginaAtual + 1)}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tab: Papéis */}
          <TabsContent value="papeis" className="space-y-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Gerenciar Papéis</CardTitle>
                  <CardDescription>
                    Crie e customize papéis com permissões específicas
                  </CardDescription>
                </div>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Novo Papel
                </Button>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {papeis.map((papel) => (
                    <Card key={papel.codigo} className="border">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-base">{papel.nome}</CardTitle>
                            <CardDescription className="text-xs mt-1">
                              {papel.descricao}
                            </CardDescription>
                          </div>
                          {papel.customizado && (
                            <Badge variant="secondary">Customizado</Badge>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-2">
                            Permissões ({papel.total_permissoes})
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {papel.permissoes.slice(0, 5).map((perm) => (
                              <Badge key={perm} variant="outline" className="text-xs">
                                {perm}
                              </Badge>
                            ))}
                            {papel.permissoes.length > 5 && (
                              <Badge variant="outline" className="text-xs">
                                +{papel.permissoes.length - 5}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2 pt-2">
                          <Button size="sm" variant="outline" className="flex-1">
                            <Edit2 className="w-3 h-3 mr-1" />
                            Editar
                          </Button>
                          {papel.customizado && (
                            <Button size="sm" variant="outline" className="flex-1">
                              <Trash2 className="w-3 h-3 mr-1" />
                              Deletar
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Tab: Permissões */}
          <TabsContent value="permissoes" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Permissões do Sistema</CardTitle>
                <CardDescription>
                  Visualize todas as permissões disponíveis agrupadas por categoria
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {Object.entries(
                    permissoes.reduce((acc: Record<string, Permissao[]>, perm) => {
                      const cat = perm.categoria;
                      if (!acc[cat]) acc[cat] = [];
                      acc[cat].push(perm);
                      return acc;
                    }, {})
                  ).map(([categoria, perms]) => (
                    <div key={categoria}>
                      <h3 className="font-semibold mb-3 capitalize">{categoria}</h3>
                      <div className="space-y-2">
                        {perms.map((perm) => (
                          <div key={perm.codigo} className="flex items-start gap-3 p-3 border rounded-lg">
                            <div className="flex-1">
                              <p className="font-medium text-sm">{perm.nome}</p>
                              <p className="text-xs text-muted-foreground">{perm.descricao}</p>
                            </div>
                            <Badge variant="outline" className="text-xs">
                              {perm.codigo}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Rodapé */}
      <div className="text-center mt-12 text-xs text-muted-foreground">
        <p>Criado por Eng. Anibal Nisgoski</p>
      </div>
    </div>
  );
}
