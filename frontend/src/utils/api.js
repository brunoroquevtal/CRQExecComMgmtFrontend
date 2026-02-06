import axios from 'axios';

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

// Interceptor para requisições - não definir Content-Type para FormData
api.interceptors.request.use(
  (config) => {
    // Se for FormData, remover Content-Type para o browser definir automaticamente
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
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
    if (error.response) {
      // Erro com resposta do servidor
      console.error('Erro da API:', error.response.status, error.response.data);
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
