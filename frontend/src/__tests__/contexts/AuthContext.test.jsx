import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';
import api from '../../utils/api';
import { toast } from 'react-hot-toast';

// Mock das dependências
vi.mock('../../utils/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}));

vi.mock('react-hot-toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}));

const wrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>{children}</AuthProvider>
  </BrowserRouter>
);

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('deve fazer login com sucesso', async () => {
      const mockResponse = {
        data: {
          success: true,
          access_token: 'test-token',
          user: { id: '123', email: 'test@vtal.com' }
        }
      };

      api.post.mockResolvedValueOnce(mockResponse);
      api.get.mockResolvedValueOnce({
        data: { id: '123', email: 'test@vtal.com', role: 'visualizador' }
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await act(async () => {
        const success = await result.current.login('test@vtal.com', 'password123');
        expect(success).toBe(true);
      });

      expect(localStorage.getItem('auth_token')).toBe('test-token');
      expect(toast.success).toHaveBeenCalledWith('Login realizado com sucesso!');
    });

    it('deve falhar com credenciais inválidas', async () => {
      api.post.mockRejectedValueOnce({
        response: { status: 401, data: { error: 'Email ou senha incorretos' } }
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await act(async () => {
        const success = await result.current.login('test@vtal.com', 'wrong');
        expect(success).toBe(false);
      });

      expect(toast.error).toHaveBeenCalled();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('signup', () => {
    it('deve fazer cadastro com sucesso', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Cadastro realizado! Verifique seu email para confirmar a conta.'
        }
      };

      api.post.mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await act(async () => {
        const success = await result.current.signup('new@vtal.com', 'password123', 'Nome Completo');
        expect(success).toBe(true);
      });

      expect(toast.success).toHaveBeenCalled();
    });

    it('deve falhar com email já cadastrado', async () => {
      api.post.mockRejectedValueOnce({
        response: { status: 400, data: { error: 'Este email já está cadastrado' } }
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await act(async () => {
        const success = await result.current.signup('existing@vtal.com', 'password123', 'Nome');
        expect(success).toBe(false);
      });

      expect(toast.error).toHaveBeenCalled();
    });
  });

  describe('logout', () => {
    it('deve fazer logout e limpar localStorage', async () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('auth_user', JSON.stringify({ id: '123', email: 'test@vtal.com' }));

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(toast.success).toHaveBeenCalledWith('Logout realizado com sucesso!');
    });
  });

  describe('hasRole', () => {
    it('deve retornar true para administrador', async () => {
      localStorage.setItem('auth_token', 'test-token');
      api.get.mockResolvedValueOnce({
        data: { id: '123', role: 'administrador' }
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await waitFor(() => {
        expect(result.current.profile).toBeTruthy();
      });

      expect(result.current.hasRole('visualizador')).toBe(true);
      expect(result.current.hasRole('lider_mudanca')).toBe(true);
    });

    it('deve retornar false para role diferente', async () => {
      localStorage.setItem('auth_token', 'test-token');
      api.get.mockResolvedValueOnce({
        data: { id: '123', role: 'visualizador' }
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper
      });

      await waitFor(() => {
        expect(result.current.profile).toBeTruthy();
      });

      expect(result.current.hasRole('administrador')).toBe(false);
      expect(result.current.hasRole('visualizador')).toBe(true);
    });
  });
});
