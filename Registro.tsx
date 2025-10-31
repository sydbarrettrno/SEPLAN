import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { AlertCircle, Lock, Mail, Loader2, Shield, User, Building } from 'lucide-react';
import { toast } from 'sonner';
import { useLocation } from 'wouter';

export default function Registro() {
  const [, setLocation] = useLocation();
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    senha: '',
    confirmaSenha: '',
    organizacao: '',
  });
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRegistro = async (e: React.FormEvent) => {
    e.preventDefault();
    setErro('');

    // Validações
    if (!formData.nome || !formData.email || !formData.senha) {
      setErro('Preencha todos os campos obrigatórios');
      return;
    }

    if (formData.senha !== formData.confirmaSenha) {
      setErro('As senhas não correspondem');
      return;
    }

    if (formData.senha.length < 8) {
      setErro('A senha deve ter pelo menos 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/registro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome: formData.nome,
          email: formData.email,
          senha: formData.senha,
          organizacao: formData.organizacao || 'Não informado',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast.success('Registro realizado com sucesso! Faça login para continuar.');
        setLocation('/login');
      } else {
        const data = await response.json();
        setErro(data.detalhe || 'Erro ao registrar');
        toast.error(data.detalhe || 'Erro ao registrar');
      }
    } catch (error) {
      setErro('Erro ao conectar ao servidor');
      toast.error('Erro ao conectar ao servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Logo e Título */}
        <div className="text-center space-y-2">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-600 p-3 rounded-lg">
              <Shield className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-white">
            Sistema Analítico
          </h1>
          <p className="text-slate-400">
            Crie sua conta
          </p>
        </div>

        {/* Card de Registro */}
        <Card className="border-slate-700 bg-slate-800">
          <CardHeader className="space-y-1">
            <CardTitle className="text-white">Novo Registro</CardTitle>
            <CardDescription>
              Preencha os dados para criar sua conta
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleRegistro} className="space-y-4">
              {/* Nome */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Nome Completo
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="text"
                    name="nome"
                    placeholder="Seu nome"
                    value={formData.nome}
                    onChange={handleChange}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>
              </div>

              {/* Email */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="email"
                    name="email"
                    placeholder="seu@email.com"
                    value={formData.email}
                    onChange={handleChange}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>
              </div>

              {/* Organização */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Organização (Opcional)
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="text"
                    name="organizacao"
                    placeholder="Sua empresa"
                    value={formData.organizacao}
                    onChange={handleChange}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                  />
                </div>
              </div>

              {/* Senha */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="password"
                    name="senha"
                    placeholder="••••••••"
                    value={formData.senha}
                    onChange={handleChange}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>
              </div>

              {/* Confirmar Senha */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Confirmar Senha
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="password"
                    name="confirmaSenha"
                    placeholder="••••••••"
                    value={formData.confirmaSenha}
                    onChange={handleChange}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                    required
                  />
                </div>
              </div>

              {/* Erro */}
              {erro && (
                <div className="flex gap-2 p-3 bg-red-900/20 border border-red-700 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-400">{erro}</p>
                </div>
              )}

              {/* Botão de Registro */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Registrando...
                  </>
                ) : (
                  'Criar Conta'
                )}
              </Button>

              {/* Link para Login */}
              <div className="text-center text-sm">
                <p className="text-slate-400">
                  Já tem conta?{' '}
                  <button
                    type="button"
                    onClick={() => setLocation('/login')}
                    className="text-blue-400 hover:text-blue-300 font-medium"
                  >
                    Faça login aqui
                  </button>
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Crédito Autoral */}
        <div className="text-center text-xs text-slate-500">
          <p>Criado por Eng. Anibal Nisgoski</p>
        </div>
      </div>
    </div>
  );
}
