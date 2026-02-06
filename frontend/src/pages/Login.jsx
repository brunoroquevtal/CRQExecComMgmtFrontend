import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simular delay de autenticação
    await new Promise(resolve => setTimeout(resolve, 500));

    if (login(username, password)) {
      navigate('/dashboard');
    } else {
      setError('Usuário ou senha inválidos');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-vtal-primary via-vtal-secondary to-vtal-dark flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-display font-bold text-vtal-gray-800 mb-2">🚀</h1>
          <h2 className="text-2xl font-display font-bold text-vtal-gray-800">Janela de Mudança TI</h2>
          <p className="text-vtal-gray-600 mt-2">Faça login para continuar</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Usuário
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent transition-all"
              placeholder="Digite seu usuário"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Senha
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent transition-all"
              placeholder="Digite sua senha"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-vtal-secondary to-vtal-primary hover:from-vtal-primary hover:to-vtal-dark text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-vtal-gray-200">
          <p className="text-sm text-vtal-gray-600 text-center mb-2">Usuários de teste:</p>
          <div className="bg-vtal-gray-50 rounded-lg p-4 space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="font-medium">admin</span>
              <span className="text-vtal-gray-500">admin123</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">lider</span>
              <span className="text-vtal-gray-500">lider123</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">visualizador</span>
              <span className="text-vtal-gray-500">view123</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
