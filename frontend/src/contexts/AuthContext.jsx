import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Verificar se há usuário salvo no localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
      setIsAuthenticated(true);
    }
  }, []);

  const login = (username, password) => {
    // Autenticação simples (substituir por chamada à API)
    const users = {
      admin: { name: 'Administrador', type: 'admin', password: 'admin123' },
      lider: { name: 'Líder', type: 'lider', password: 'lider123' },
      visualizador: { name: 'Visualizador', type: 'visualizador', password: 'view123' }
    };

    const user = users[username];
    if (user && user.password === password) {
      setUser({ username, ...user });
      setIsAuthenticated(true);
      localStorage.setItem('user', JSON.stringify({ username, ...user }));
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
