import React, { createContext, useContext, useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import api from '../utils/api';

const AuthContext = createContext();

// Inicializar cliente Supabase
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

let supabase = null;
if (supabaseUrl && supabaseAnonKey) {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
} else {
  console.warn('[AUTH] Supabase não configurado. Configure VITE_SUPABASE_URL e VITE_SUPABASE_ANON_KEY');
}

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
      setLoading(false);
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
  const loadUserProfile = async (userId) => {
    try {
      // Adicionar token ao header da API
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setLoading(false);
        return;
      }

      // Buscar perfil via API do backend
      const response = await api.get('/auth/profile', {
        headers: {
          Authorization: `Bearer ${session.access_token}`
        }
      });

      setProfile(response.data);
      setIsAuthenticated(true);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
      // Se erro 401, fazer logout
      if (error.response?.status === 401) {
        await logout();
      }
      setLoading(false);
    }
  };

  // Login com email e senha
  const login = async (email, password) => {
    if (!supabase) {
      toast.error('Supabase não configurado');
      return false;
    }

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        toast.error(error.message);
        return false;
      }

      setUser(data.user);
      await loadUserProfile(data.user.id);
      toast.success('Login realizado com sucesso!');
      return true;
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      toast.error('Erro ao fazer login');
      return false;
    }
  };

  // Cadastro de novo usuário
  const signup = async (email, password, fullName) => {
    if (!supabase) {
      toast.error('Supabase não configurado');
      return false;
    }

    try {
      // Validar domínio antes de cadastrar
      const validateResponse = await api.post('/auth/signup', { email });
      if (!validateResponse.data.success) {
        toast.error(validateResponse.data.error || 'Domínio não permitido');
        return false;
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
      const errorMessage = error.response?.data?.error || 'Erro ao fazer cadastro';
      toast.error(errorMessage);
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
