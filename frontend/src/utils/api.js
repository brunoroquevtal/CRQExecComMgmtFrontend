import axios from 'axios';
import supabase from './supabase';

// URL base da API - usa variável de ambiente ou padrão relativo
// Se VITE_API_URL não estiver definida, usa '/api' (proxy do Vite em desenvolvimento)
// Em produção, defina VITE_API_URL com a URL completa do backend
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Criar instância do axios com configuração base
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 300000 // 5 minutos (para uploads grandes)
});

// Interceptor para requisições - adicionar token de autenticação
api.interceptors.request.use(
  async (config) => {
    // Se for FormData, remover Content-Type para o browser definir automaticamente
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    // Adicionar token de autenticação se disponível
    if (supabase) {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session?.access_token) {
          config.headers.Authorization = `Bearer ${session.access_token}`;
        }
      } catch (error) {
        console.warn('Erro ao obter token:', error);
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Não logar erros 404 para endpoints opcionais (como /auth/allowed-domains)
    // Apenas logar em modo debug ou para outros status codes
    if (error.response) {
      const status = error.response.status;
      // Logar apenas erros que não sejam 404 (endpoint não encontrado)
      if (status !== 404) {
        console.error('Erro da API:', status, error.response.data);
      }
    } else if (error.request) {
      // Erro de rede (sem resposta)
      console.error('Erro de rede:', error.message);
    } else {
      // Outro tipo de erro
      console.error('Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
