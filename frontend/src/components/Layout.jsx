import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Layout() {
  const { profile, roleLabel, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false); // Fechado por padrão em mobile
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/dados', label: 'Dados', icon: '✏️' },
    { path: '/planejamento', label: 'Planejamento', icon: '📅' },
    { path: '/comunicacao', label: 'Comunicação', icon: '💬' },
    { path: '/configuracoes', label: 'Configurações', icon: '⚙️' }
  ];

  const roleLabels = {
    administrador: 'Administrador',
    lider_mudanca: 'Líder da Mudança',
    visualizador: 'Visualizador'
  };

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-50">
      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="md:hidden fixed top-4 left-4 z-50 bg-vtal-primary text-white p-2 rounded-lg shadow-lg"
      >
        {mobileMenuOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <aside className={`
        bg-gradient-to-b from-vtal-primary to-vtal-dark text-white 
        transition-all duration-300 
        fixed md:relative z-40
        ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        ${sidebarOpen ? 'w-64' : 'w-20'} 
        h-full
        flex flex-col shadow-lg
      `}>
        {/* Header */}
        <div className="p-4 border-b border-vtal-dark/50 flex items-center justify-between">
          <h1 className={`font-display font-bold text-lg md:text-xl transition-opacity ${sidebarOpen ? 'opacity-100' : 'opacity-0 w-0'}`}>
            🚀 Janela de Mudança TI
          </h1>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="hidden md:block p-2 rounded-lg hover:bg-vtal-dark/50 transition-colors"
            title={sidebarOpen ? 'Recolher' : 'Expandir'}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        {/* User Info */}
        <div className={`p-4 border-b border-vtal-dark/50 ${(sidebarOpen || mobileMenuOpen) ? '' : 'text-center'}`}>
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 rounded-full bg-vtal-secondary flex items-center justify-center font-bold">
              {profile?.full_name?.charAt(0) || profile?.email?.charAt(0) || 'U'}
            </div>
            {(sidebarOpen || mobileMenuOpen) && (
              <div className="flex-1 min-w-0">
                <p className="font-semibold truncate">{profile?.full_name || profile?.email || 'Usuário'}</p>
                <p className="text-sm text-vtal-light/80 truncate">{roleLabel || 'Usuário'}</p>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-2">
          {menuItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg mb-2 transition-all duration-200 ${
                location.pathname === item.path
                  ? 'bg-vtal-secondary text-white shadow-lg'
                  : 'text-vtal-light/90 hover:bg-vtal-dark/50 hover:text-white'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              {(sidebarOpen || mobileMenuOpen) && <span className="font-medium">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-vtal-dark/50">
          <button
            onClick={logout}
            className="w-full bg-vtal-danger hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            <span>🚪</span>
            {(sidebarOpen || mobileMenuOpen) && <span>Sair</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-vtal-gray-50 md:ml-0">
        <div className="p-3 md:p-6 pt-16 md:pt-6">
          <Outlet />
        </div>
      </main>
      
      {/* Overlay para mobile */}
      {mobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
    </div>
  );
}

export default Layout;
