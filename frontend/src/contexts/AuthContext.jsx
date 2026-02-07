import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../utils/api';
import supabase from '../utils/supabase';

const AuthContext = createContext();

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
    if (!supabase) {
      // Se Supabase não estiver configurado, permitir acesso sem autenticação
      // (modo de desenvolvimento ou quando autenticação não é necessária)
      setLoading(false);
      setIsAuthenticated(true); // Permitir acesso sem autenticação
      // Não definir perfil - a aplicação funcionará sem roles específicas
      return;
    }

    // Verificar sessão atual
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setUser(session.user);
        loadUserProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    // Escutar mudanças de autenticação
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        setUser(session.user);
        loadUserProfile(session.user.id);
      } else {
        setUser(null);
        setProfile(null);
        setIsAuthenticated(false);
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Carregar perfil do usuário via API do backend
  const loadUserProfile = async (userId) => {
    try {
      // Obter sessão do Supabase para pegar o token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setLoading(false);
        return;
      }

      // Buscar perfil via API do backend
      try {
        const response = await api.get('/auth/profile', {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        });

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

        // Se erro 404 ou 500, usar perfil padrão baseado nos dados do Supabase Auth
        if (profileError.response?.status === 404 || profileError.response?.status === 500) {
          console.warn('Endpoint /api/auth/profile não disponível. Usando perfil padrão.');
          const defaultProfile = {
            id: session.user.id,
            email: session.user.email,
            full_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Usuário',
            role: 'visualizador'
          };
          setProfile(defaultProfile);
          setIsAuthenticated(true);
          setLoading(false);
          return;
        }

        // Outro erro - usar perfil padrão
        console.error('Erro ao carregar perfil do backend:', profileError.message);
        const defaultProfile = {
          id: session.user.id,
          email: session.user.email,
          full_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Usuário',
          role: 'visualizador'
        };
        setProfile(defaultProfile);
        setIsAuthenticated(true);
        setLoading(false);
      }
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
      // Em caso de erro, permitir acesso com perfil padrão se tiver sessão
      if (supabase) {
        try {
          const { data: { session } } = await supabase.auth.getSession();
          if (session) {
            const defaultProfile = {
              id: session.user.id,
              email: session.user.email,
              full_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Usuário',
              role: 'visualizador'
            };
            setProfile(defaultProfile);
            setIsAuthenticated(true);
          }
        } catch (sessionError) {
          // Ignorar erro
        }
      }
      setLoading(false);
    }
  };

  // Login com email e senha
  const login = async (email, password) => {
    if (!supabase) {
      toast.error('Autenticação não disponível. Configure o Supabase para usar login/senha.');
      return false;
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        // Mensagens de erro mais amigáveis
        let errorMessage = error.message;
        if (error.message.includes('Invalid login credentials')) {
          errorMessage = 'Email ou senha incorretos';
        } else if (error.message.includes('Email not confirmed')) {
          errorMessage = 'Por favor, confirme seu email antes de fazer login';
        }
        toast.error(errorMessage);
        return false;
      }

      setUser(data.user);
      await loadUserProfile(data.user.id);
      toast.success('Login realizado com sucesso!');
      return true;
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      toast.error('Erro ao fazer login. Tente novamente.');
      return false;
    }
  };

  // Cadastro de novo usuário
  const signup = async (email, password, fullName) => {
    if (!supabase) {
      toast.error('Autenticação não disponível. Configure o Supabase para criar contas.');
      return false;
    }

    try {
      // Validar domínio antes de cadastrar (opcional - se endpoint não existir, continua)
      try {
        const validateResponse = await api.post('/auth/signup', { email });
        if (validateResponse.data && !validateResponse.data.success) {
          toast.error(validateResponse.data.error || 'Domínio não permitido');
          return false;
        }
      } catch (validationError) {
        // Se o endpoint não existir (404), continuar sem validação
        // Isso permite que o cadastro funcione mesmo sem o backend configurado
        if (validationError.response?.status !== 404) {
          console.warn('Erro ao validar domínio (continuando sem validação):', validationError.message);
        }
        // Continuar com o cadastro mesmo sem validação de domínio
      }

      // Cadastrar no Supabase Auth
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) {
        toast.error(error.message);
        return false;
      }

      if (data.user) {
        toast.success('Cadastro realizado! Verifique seu email para confirmar a conta.');
        return true;
      }

      return false;
    } catch (error) {
      console.error('Erro ao fazer cadastro:', error);
      // Se for erro do Supabase, já foi tratado acima
      // Se for outro erro, mostrar mensagem genérica
      if (!error.message || !error.message.includes('auth')) {
        toast.error('Erro ao fazer cadastro. Tente novamente.');
      }
      return false;
    }
  };

  // Logout
  const logout = async () => {
    if (!supabase) {
      setUser(null);
      setProfile(null);
      setIsAuthenticated(false);
      navigate('/login');
      return;
    }

    try {
      await supabase.auth.signOut();
      setUser(null);
      setProfile(null);
      setIsAuthenticated(false);
      navigate('/login');
      toast.success('Logout realizado com sucesso!');
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
      // Mesmo com erro, limpar estado local
      setUser(null);
      setProfile(null);
      setIsAuthenticated(false);
      navigate('/login');
    }
  };

  // Obter token de acesso
  const getAccessToken = async () => {
    if (!supabase || !user) {
      return null;
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      return session?.access_token || null;
    } catch (error) {
      console.error('Erro ao obter token:', error);
      return null;
    }
  };

  // Verificar se usuário tem role específica
  const hasRole = (requiredRole) => {
    // Se Supabase não estiver configurado, permitir acesso (modo desenvolvimento)
    if (!supabase) return true;
    
    if (!profile) return false;
    
    // Administrador tem acesso a tudo
    if (profile.role === 'administrador') return true;
    
    // Verificar role específica
    return profile.role === requiredRole;
  };

  // Verificar se usuário tem uma das roles
  const hasAnyRole = (requiredRoles) => {
    // Se Supabase não estiver configurado, permitir acesso (modo desenvolvimento)
    if (!supabase) return true;
    
    if (!profile) return false;
    if (profile.role === 'administrador') return true;
    return requiredRoles.includes(profile.role);
  };

  // Função para recarregar o perfil (útil após alterações)
  const reloadProfile = async () => {
    if (user?.id) {
      await loadUserProfile(user.id);
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
