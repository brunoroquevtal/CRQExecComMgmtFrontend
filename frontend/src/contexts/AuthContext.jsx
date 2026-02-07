import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../utils/api';

const AuthContext = createContext();

// Chave para armazenar token no localStorage
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Mapear roles do backend para labels
  const roleLabels = {
    administrador: 'Administrador',
    lider_mudanca: 'Líder da Mudança',
    visualizador: 'Visualizador'
  };

  // Verificar sessão ao carregar
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (token && storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        setUser(userData);
        // Carregar perfil do backend
        loadUserProfile();
      } catch (error) {
        console.error('Erro ao restaurar sessão:', error);
        // Limpar dados inválidos
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setLoading(false);
      }
    } else {
      setLoading(false);
    }
  }, []);

  // Carregar perfil do usuário via API do backend
  // NÃO usa mais consulta direta ao Supabase (user_profiles)
  // Usa: GET /api/auth/profile (endpoint do backend)
  const loadUserProfile = async () => {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        setLoading(false);
        return;
      }

      // Buscar perfil via API do backend (não mais diretamente do Supabase)
      try {
        const response = await api.get('/auth/profile');

        // Perfil obtido com sucesso do backend
        setProfile(response.data);
        setIsAuthenticated(true);
        setLoading(false);
        return;
      } catch (profileError) {
        // Se erro 401, fazer logout
        if (profileError.response?.status === 401) {
          await logout();
          return;
        }

        // Se erro 404 ou 500, usar perfil padrão baseado nos dados do usuário armazenado
        if (profileError.response?.status === 404 || profileError.response?.status === 500) {
          console.warn('Endpoint /api/auth/profile não disponível. Usando perfil padrão.');
          const storedUser = localStorage.getItem(USER_KEY);
          if (storedUser) {
            try {
              const userData = JSON.parse(storedUser);
              const defaultProfile = {
                id: userData.id,
                email: userData.email,
                full_name: userData.email?.split('@')[0] || 'Usuário',
                role: 'visualizador'
              };
              setProfile(defaultProfile);
              setIsAuthenticated(true);
              setLoading(false);
              return;
            } catch (e) {
              // Ignorar erro de parse
            }
          }
        }

        // Outro erro - usar perfil padrão
        console.error('Erro ao carregar perfil do backend:', profileError.message);
        const storedUser = localStorage.getItem(USER_KEY);
        if (storedUser) {
          try {
            const userData = JSON.parse(storedUser);
            const defaultProfile = {
              id: userData.id,
              email: userData.email,
              full_name: userData.email?.split('@')[0] || 'Usuário',
              role: 'visualizador'
            };
            setProfile(defaultProfile);
            setIsAuthenticated(true);
          } catch (e) {
            // Ignorar erro
          }
        }
        setLoading(false);
      }
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
      setLoading(false);
    }
  };

  // Login com email e senha via API do backend
  // NÃO usa mais Supabase diretamente
  // Usa: POST /api/auth/login (endpoint do backend)
  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      if (response.data.success && response.data.access_token) {
        // Armazenar token e dados do usuário
        const token = response.data.access_token;
        const userData = response.data.user;

        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));

        setUser(userData);
        
        // Carregar perfil do backend
        await loadUserProfile();
        
        toast.success('Login realizado com sucesso!');
        return true;
      } else {
        toast.error('Erro ao fazer login. Resposta inválida do servidor.');
        return false;
      }
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      
      // Mensagens de erro mais amigáveis
      let errorMessage = 'Erro ao fazer login. Tente novamente.';
      
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        
        if (status === 401) {
          if (errorData?.error) {
            if (errorData.error.includes('incorretos') || errorData.error.includes('Invalid')) {
              errorMessage = 'Email ou senha incorretos';
            } else if (errorData.error.includes('não confirmado') || errorData.error.includes('not confirmed')) {
              errorMessage = 'Por favor, confirme seu email antes de fazer login';
            } else {
              errorMessage = errorData.error;
            }
          } else {
            errorMessage = 'Email ou senha incorretos';
          }
        } else if (status === 503) {
          errorMessage = 'Serviço de autenticação indisponível. Tente novamente mais tarde.';
        } else if (errorData?.error) {
          errorMessage = errorData.error;
        }
      }
      
      toast.error(errorMessage);
      return false;
    }
  };

  // Cadastro de novo usuário via API do backend
  // NÃO usa mais Supabase diretamente
  // Usa: POST /api/auth/signup (endpoint do backend)
  const signup = async (email, password, fullName) => {
    try {
      const response = await api.post('/auth/signup', {
        email,
        password,
        full_name: fullName
      });

      if (response.data.success) {
        toast.success(response.data.message || 'Cadastro realizado! Verifique seu email para confirmar a conta.');
        return true;
      } else {
        toast.error(response.data.error || 'Erro ao fazer cadastro');
        return false;
      }
    } catch (error) {
      console.error('Erro ao fazer cadastro:', error);
      
      // Mensagens de erro mais amigáveis
      let errorMessage = 'Erro ao fazer cadastro. Tente novamente.';
      
      if (error.response) {
        const status = error.response.status;
        const errorData = error.response.data;
        
        if (status === 400 || status === 403) {
          if (errorData?.error) {
            if (errorData.error.includes('já está cadastrado') || errorData.error.includes('already registered')) {
              errorMessage = 'Este email já está cadastrado';
            } else if (errorData.error.includes('não permitido') || errorData.error.includes('not allowed')) {
              errorMessage = errorData.error;
            } else if (errorData.error.includes('Senha') || errorData.error.includes('Password')) {
              errorMessage = errorData.error;
            } else {
              errorMessage = errorData.error;
            }
          } else {
            errorMessage = 'Dados inválidos. Verifique email e senha.';
          }
        } else if (status === 503) {
          errorMessage = 'Serviço de cadastro indisponível. Tente novamente mais tarde.';
        } else if (errorData?.error) {
          errorMessage = errorData.error;
        }
      }
      
      toast.error(errorMessage);
      return false;
    }
  };

  // Logout
  const logout = async () => {
    try {
      // Limpar dados do localStorage
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      
      setUser(null);
      setProfile(null);
      setIsAuthenticated(false);
      navigate('/login');
      toast.success('Logout realizado com sucesso!');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      // Mesmo com erro, limpar estado local
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setUser(null);
      setProfile(null);
      setIsAuthenticated(false);
      navigate('/login');
    }
  };

  // Obter token de acesso
  const getAccessToken = async () => {
    if (!user) {
      return null;
    }

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      return token || null;
    } catch (error) {
      console.error('Erro ao obter token:', error);
      return null;
    }
  };

  // Verificar se usuário tem role específica
  const hasRole = (requiredRole) => {
    if (!profile) return false;
    
    // Administrador tem acesso a tudo
    if (profile.role === 'administrador') return true;
    
    // Verificar role específica
    return profile.role === requiredRole;
  };

  // Verificar se usuário tem uma das roles
  const hasAnyRole = (requiredRoles) => {
    if (!profile) return false;
    if (profile.role === 'administrador') return true;
    return requiredRoles.includes(profile.role);
  };

  // Função para recarregar o perfil (útil após alterações)
  const reloadProfile = async () => {
    if (user?.id) {
      await loadUserProfile();
    }
  };

  const value = {
    user,
    profile,
    isAuthenticated,
    loading,
    login,
    signup,
    logout,
    getAccessToken,
    hasRole,
    hasAnyRole,
    reloadProfile,
    roleLabel: profile ? roleLabels[profile.role] || profile.role : null,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
}
