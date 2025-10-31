import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/_core/hooks/useAuth';
import { useLocation } from 'wouter';
import { Shield, LogOut, User, Settings, Menu, X } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const [, setLocation] = useLocation();
  const [menuAberto, setMenuAberto] = useState(false);

  const handleLogout = async () => {
    await logout();
    setLocation('/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo e Título */}
          <div
            className="flex items-center gap-2 cursor-pointer hover:opacity-80"
            onClick={() => setLocation('/')}
          >
            <div className="bg-blue-600 p-2 rounded-lg">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-gray-900">Sistema Analítico</h1>
              <p className="text-xs text-gray-500">Criado por Eng. Anibal Nisgoski</p>
            </div>
          </div>

          {/* Menu Desktop */}
          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <>
                {/* Links de Navegação */}
                <Button
                  variant="ghost"
                  onClick={() => setLocation('/')}
                  className="text-gray-700 hover:text-gray-900"
                >
                  Home
                </Button>

                {/* Admin Link */}
                {user.role === 'admin' && (
                  <Button
                    variant="ghost"
                    onClick={() => setLocation('/admin')}
                    className="text-gray-700 hover:text-gray-900"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}

                {/* Menu do Usuário */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" className="gap-2">
                      <User className="w-4 h-4" />
                      {user.name || 'Usuário'}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem className="text-xs text-gray-500">
                      {user.email}
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={() => setLocation('/perfil')}>
                      <User className="w-4 h-4 mr-2" />
                      Meu Perfil
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={handleLogout}
                      className="text-red-600"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Sair
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => setLocation('/login')}
                >
                  Login
                </Button>
                <Button
                  onClick={() => setLocation('/registro')}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Registrar
                </Button>
              </>
            )}
          </div>

          {/* Menu Mobile */}
          <div className="md:hidden">
            <button
              onClick={() => setMenuAberto(!menuAberto)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              {menuAberto ? (
                <X className="w-6 h-6" />
              ) : (
                <Menu className="w-6 h-6" />
              )}
            </button>
          </div>
        </div>

        {/* Menu Mobile Expandido */}
        {menuAberto && (
          <div className="md:hidden pb-4 space-y-2">
            {user ? (
              <>
                <Button
                  variant="ghost"
                  onClick={() => {
                    setLocation('/');
                    setMenuAberto(false);
                  }}
                  className="w-full justify-start text-gray-700"
                >
                  Home
                </Button>

                {user.role === 'admin' && (
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setLocation('/admin');
                      setMenuAberto(false);
                    }}
                    className="w-full justify-start text-gray-700"
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Admin
                  </Button>
                )}

                <Button
                  variant="ghost"
                  onClick={() => {
                    setLocation('/perfil');
                    setMenuAberto(false);
                  }}
                  className="w-full justify-start text-gray-700"
                >
                  <User className="w-4 h-4 mr-2" />
                  Meu Perfil
                </Button>

                <Button
                  variant="ghost"
                  onClick={() => {
                    handleLogout();
                    setMenuAberto(false);
                  }}
                  className="w-full justify-start text-red-600"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => {
                    setLocation('/login');
                    setMenuAberto(false);
                  }}
                  className="w-full"
                >
                  Login
                </Button>
                <Button
                  onClick={() => {
                    setLocation('/registro');
                    setMenuAberto(false);
                  }}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  Registrar
                </Button>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
