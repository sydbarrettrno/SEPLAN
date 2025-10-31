import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { AlertCircle, Lock, Mail, Loader2, Shield } from 'lucide-react';
import { toast } from 'sonner';
import { useLocation } from 'wouter';

export default function Login() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErro('');

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Armazenar token
        localStorage.setItem('access_token', data.token.access_token);
        localStorage.setItem('refresh_token', data.token.refresh_token);
        localStorage.setItem('usuario', JSON.stringify(data.token.usuario));

        toast.success(`Bem-vindo, ${data.token.usuario.nome}!`);
        
        // Redirecionar para dashboard
        setLocation('/');
      } else {
        const data = await response.json();
        setErro(data.detalhe || 'Erro ao fazer login');
        toast.error(data.detalhe || 'Erro ao fazer login');
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
            Análise Técnica com IA
          </p>
        </div>

        {/* Card de Login */}
        <Card className="border-slate-700 bg-slate-800">
          <CardHeader className="space-y-1">
            <CardTitle className="text-white">Fazer Login</CardTitle>
            <CardDescription>
              Entre com suas credenciais para acessar o sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              {/* Email */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-200">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-slate-500" />
                  <Input
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-slate-500"
                    required
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
                    placeholder="••••••••"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
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

              {/* Botão de Login */}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Entrando...
                  </>
                ) : (
                  'Fazer Login'
                )}
              </Button>

              {/* Links */}
              <div className="text-center space-y-2 text-sm">
                <p className="text-slate-400">
                  Não tem conta?{' '}
                  <button
                    type="button"
                    onClick={() => setLocation('/registro')}
                    className="text-blue-400 hover:text-blue-300 font-medium"
                  >
                    Registre-se aqui
                  </button>
                </p>
                <button
                  type="button"
                  className="text-slate-500 hover:text-slate-400 font-medium"
                >
                  Esqueceu a senha?
                </button>
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
