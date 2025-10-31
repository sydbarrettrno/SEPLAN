import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Navbar from "@/components/Navbar";
import { Shield, Zap, BarChart3, Lock, ArrowRight, CheckCircle } from "lucide-react";
import { useLocation } from "wouter";

export default function Home() {
  const { user } = useAuth();
  const [, setLocation] = useLocation();

  // Se não está autenticado, mostrar landing page
  if (!user) {
    return (
      <>
        <Navbar />
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
          {/* Hero Section */}
          <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div className="text-center space-y-6 mb-16">
              <div className="flex justify-center mb-4">
                <div className="bg-blue-600 p-4 rounded-lg">
                  <Shield className="w-12 h-12 text-white" />
                </div>
              </div>
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
                Sistema Analítico de IA
              </h1>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Análise técnica inteligente com IA, regras determinísticas e relatórios ABNT
              </p>
              <p className="text-sm text-gray-500">
                Criado por Eng. Anibal Nisgoski
              </p>
              <div className="flex gap-4 justify-center pt-4">
                <Button
                  size="lg"
                  onClick={() => setLocation('/login')}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Fazer Login
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => setLocation('/registro')}
                >
                  Criar Conta
                </Button>
              </div>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mt-20">
              <Card>
                <CardHeader>
                  <Zap className="w-8 h-8 text-blue-600 mb-2" />
                  <CardTitle>Análise Rápida</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">
                    Análise técnica em tempo real com IA integrada
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <BarChart3 className="w-8 h-8 text-blue-600 mb-2" />
                  <CardTitle>Relatórios ABNT</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">
                    Gere relatórios profissionais em DOCX e PDF
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <Lock className="w-8 h-8 text-blue-600 mb-2" />
                  <CardTitle>Seguro</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">
                    Autenticação JWT com controle de acesso baseado em papéis
                  </p>
                </CardContent>
              </Card>
            </div>
          </section>
        </div>
      </>
    );
  }

  // Se está autenticado, mostrar dashboard
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Bem-vindo, {user.name}!
            </h1>
            <p className="text-gray-600">
              Sistema Analítico de IA – Criado por Eng. Anibal Nisgoski
            </p>
          </div>

          {/* Cards de Ação */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Card: Nova Análise */}
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-600" />
                  Nova Análise
                </CardTitle>
                <CardDescription>
                  Iniciar uma nova análise técnica
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => setLocation('/analisar')}
                  className="w-full"
                >
                  Começar
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            {/* Card: Minhas Análises */}
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  Minhas Análises
                </CardTitle>
                <CardDescription>
                  Visualizar análises anteriores
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  variant="outline"
                  onClick={() => setLocation('/analises')}
                  className="w-full"
                >
                  Ver Histórico
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            {/* Card: Admin (se for admin) */}
            {user.role === 'admin' && (
              <Card className="hover:shadow-lg transition-shadow cursor-pointer border-blue-200 bg-blue-50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-600" />
                    Painel Admin
                  </CardTitle>
                  <CardDescription>
                    Gerenciar usuários e permissões
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button
                    onClick={() => setLocation('/admin')}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    Acessar
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Informações do Usuário */}
          <Card className="mt-12">
            <CardHeader>
              <CardTitle>Informações da Conta</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Nome</p>
                  <p className="font-medium text-gray-900">{user.name}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Email</p>
                  <p className="font-medium text-gray-900">{user.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Papel</p>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-gray-900 capitalize">
                      {user.role}
                    </p>
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Membro desde</p>
                  <p className="font-medium text-gray-900">
                    {user.createdAt ? new Date(user.createdAt).toLocaleDateString('pt-BR') : 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Crédito Autoral */}
          <div className="text-center mt-12 text-sm text-gray-500">
            <p>Criado por Eng. Anibal Nisgoski</p>
          </div>
        </div>
      </div>
    </>
  );
}
