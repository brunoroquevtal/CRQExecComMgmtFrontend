import axios from 'axios';

// URL base da API - usa variável de ambiente ou padrão relativo
// Se VITE_API_URL não estiver definida, usa '/api' (proxy do Vite em desenvolvimento)
// Em produção, defina VITE_API_URL com a URL completa do backend
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Chave para armazenar token no localStorage
const TOKEN_KEY = 'auth_token';

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
    // Log da requisição
    console.log('[API] 📤 Requisição:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL || ''}${config.url}`,
      headers: {
        ...config.headers,
        Authorization: config.headers.Authorization ? 'Bearer ***' : 'não presente'
      }
    });

    // Se for FormData, remover Content-Type para o browser definir automaticamente
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }

    // Adicionar token de autenticação se disponível no localStorage
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
        console.log('[API] 🔑 Token adicionado à requisição (primeiros 20 chars):', token.substring(0, 20) + '...');
      } else {
        console.log('[API] ⚠️ Token não encontrado no localStorage');
      }
    } catch (error) {
      console.warn('[API] ❌ Erro ao obter token do localStorage:', error);
    }

    return config;
  },
  (error) => {
    console.error('[API] ❌ Erro no interceptor de requisição:', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => {
    // Log da resposta bem-sucedida
    console.log('[API] ✅ Resposta recebida:', {
      method: response.config.method?.toUpperCase(),
      url: response.config.url,
      status: response.status,
      statusText: response.statusText,
      data: response.data,
      headers: response.headers
    });
    return response;
  },
  (error) => {
    // Log detalhado do erro
    console.error('[API] ❌ Erro na resposta:', {
      method: error.config?.method?.toUpperCase(),
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      fullURL: `${error.config?.baseURL || ''}${error.config?.url}`,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
      message: error.message,
      request: error.request ? 'Request enviado' : 'Sem request'
    });

    // Se erro 401 (não autorizado), limpar token e redirecionar para login
    if (error.response?.status === 401) {
      console.warn('[API] ⚠️ Erro 401 - Token inválido, limpando e redirecionando...');
      // Remover token inválido
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem('auth_user');
      
      // Redirecionar para login apenas se não estiver já na página de login
      if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
        window.location.href = '/login';
      }
    }
    
    // Não logar erros 404 para endpoints opcionais (como /auth/allowed-domains)
    // Apenas logar em modo debug ou para outros status codes
    if (error.response) {
      const status = error.response.status;
      // Logar apenas erros que não sejam 404 (endpoint não encontrado)
      if (status !== 404) {
        console.error('[API] Erro da API:', status, error.response.data);
      }
    } else if (error.request) {
      // Erro de rede (sem resposta)
      console.error('[API] Erro de rede:', error.message);
    } else {
      // Outro tipo de erro
      console.error('[API] Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
