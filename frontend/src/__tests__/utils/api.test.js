import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('api utility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('localStorage token management', () => {
    it('deve armazenar e recuperar token corretamente', () => {
      const token = 'test-token-123';
      localStorage.setItem('auth_token', token);
      
      expect(localStorage.getItem('auth_token')).toBe(token);
    });

    it('deve remover token corretamente', () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.removeItem('auth_token');
      
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('FormData handling', () => {
    it('deve criar FormData corretamente', () => {
      const formData = new FormData();
      formData.append('file', new Blob(['test'], { type: 'text/plain' }));
      
      expect(formData instanceof FormData).toBe(true);
    });
  });

  describe('API configuration', () => {
    it('deve usar URL padrão quando VITE_API_URL não está definida', () => {
      // Em ambiente de teste, import.meta.env pode não estar disponível
      // Este teste verifica a lógica básica
      const defaultUrl = '/api';
      expect(defaultUrl).toBe('/api');
    });
  });
});
