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

  // Carregar perfil do usuário
  // forceSupabase: se true, busca diretamente do Supabase ignorando o backend
  const loadUserProfile = async (userId, forceSupabase = false) => {
    try {
      // Adicionar token ao header da API
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setLoading(false);
        return;
      }

      // Se forceSupabase for true, buscar diretamente do Supabase (útil após atualizações)
      if (forceSupabase) {
        try {
          const { data: supabaseProfile, error: supabaseError } = await supabase
            .from('user_profiles')
            .select('*')
            .eq('id', userId)
            .single();

          if (!supabaseError && supabaseProfile) {
            setProfile(supabaseProfile);
            setIsAuthenticated(true);
            setLoading(false);
            return;
          }
        } catch (supabaseError) {
          console.warn('Erro ao buscar perfil do Supabase:', supabaseError.message);
        }
      }

      // Tentar buscar perfil via API do backend primeiro
      try {
        const response = await api.get('/auth/profile', {
          headers: {
            Authorization: `Bearer ${session.access_token}`
          }
        });

        // Verificar se o perfil retornado tem role 'visualizador' padrão
        // Se sim, tentar buscar diretamente do Supabase para garantir que temos o role atualizado
        if (response.data && response.data.role === 'visualizador' && !forceSupabase) {
          // Tentar buscar do Supabase para verificar se há atualização
          try {
            const { data: supabaseProfile, error: supabaseError } = await supabase
              .from('user_profiles')
              .select('*')
              .eq('id', userId)
              .single();

            if (!supabaseError && supabaseProfile && supabaseProfile.role !== 'visualizador') {
              // Perfil no Supabase tem role diferente - usar ele
              setProfile(supabaseProfile);
              setIsAuthenticated(true);
              setLoading(false);
              return;
            }
          } catch (supabaseCheckError) {
            // Ignorar erro e usar perfil do backend
          }
        }

        setProfile(response.data);
        setIsAuthenticated(true);
        setLoading(false);
        return; // Sucesso, sair da função
      } catch (profileError) {
        // Se o endpoint não existir (404), tentar buscar diretamente do Supabase
        if (profileError.response?.status === 404) {
          // Endpoint não existe - buscar diretamente do Supabase
          try {
            const { data: supabaseProfile, error: supabaseError } = await supabase
              .from('user_profiles')
              .select('*')
              .eq('id', userId)
              .single();

            if (!supabaseError && supabaseProfile) {
              // Perfil encontrado no Supabase
              setProfile(supabaseProfile);
              setIsAuthenticated(true);
              setLoading(false);
              return;
            } else {
              // Erro ao buscar (tabela não existe, RLS bloqueando, etc.)
              // Usar perfil padrão baseado nos dados do Supabase Auth
              const defaultProfile = {
                id: session.user.id,
                email: session.user.email,
                full_name: session.user.user_metadata?.full_name || session.user.email?.split('@')[0] || 'Usuário',
                role: 'visualizador' // Role padrão quando perfil não existe
              };
              setProfile(defaultProfile);
              setIsAuthenticated(true);
              setLoading(false);
            }
          } catch (supabaseDirectError) {
            // Erro ao buscar do Supabase (500, tabela não existe, etc.) - usar perfil padrão
            // Não logar erro 500 para não poluir o console
            if (import.meta.env.DEV && supabaseDirectError.code !== 'PGRST116') {
              console.info('Tabela user_profiles não disponível. Usando perfil padrão.');
            }
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
        } else if (profileError.response?.status === 401) {
          // Se erro 401, fazer logout
          await logout();
        } else {
          // Outro erro - tentar buscar do Supabase diretamente
          try {
            const { data: supabaseProfile, error: supabaseError } = await supabase
              .from('user_profiles')
              .select('*')
              .eq('id', userId)
              .single();

            if (!supabaseError && supabaseProfile) {
              setProfile(supabaseProfile);
              setIsAuthenticated(true);
              setLoading(false);
            } else {
              throw new Error('Perfil não encontrado');
            }
          } catch (supabaseError) {
            // Fallback para perfil padrão (tabela não existe, RLS bloqueando, etc.)
            // Não logar erros 500 para não poluir o console
            if (import.meta.env.DEV && supabaseError.code !== 'PGRST116') {
              console.info('Erro ao carregar perfil do Supabase. Usando perfil padrão.');
            }
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
        }
      }
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
      // Se erro 401, fazer logout
      if (error.response?.status === 401) {
        await logout();
      } else {
        // Em caso de outro erro, permitir acesso com perfil padrão
        setLoading(false);
      }
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
  // forceSupabase: se true, busca diretamente do Supabase ignorando o backend
  const reloadProfile = async (forceSupabase = true) => {
    if (user?.id) {
      await loadUserProfile(user.id, forceSupabase);
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
