import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { toast } from 'react-hot-toast';

function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [allowedDomains, setAllowedDomains] = useState([]);
  const { signup } = useAuth();
  const navigate = useNavigate();

  // Carregar domínios permitidos
  useEffect(() => {
    const loadAllowedDomains = async () => {
      try {
        const response = await api.get('/auth/allowed-domains');
        setAllowedDomains(response.data.domains || []);
      } catch (error) {
        console.error('Erro ao carregar domínios:', error);
      }
    };
    loadAllowedDomains();
  }, []);

  // Validar domínio do email
  const validateEmailDomain = (email) => {
    if (allowedDomains.length === 0) return true; // Se não houver domínios configurados, permitir
    
    const domain = email.toLowerCase().split('@')[1];
    return allowedDomains.includes(domain);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validações
    if (!email || !password || !confirmPassword || !fullName) {
      setError('Todos os campos são obrigatórios');
      return;
    }

    if (password.length < 6) {
      setError('A senha deve ter pelo menos 6 caracteres');
      return;
    }

    if (password !== confirmPassword) {
      setError('As senhas não coincidem');
      return;
    }

    if (!validateEmailDomain(email)) {
      setError(`Apenas emails dos domínios permitidos podem se cadastrar: ${allowedDomains.join(', ')}`);
      return;
    }

    setLoading(true);

    try {
      const success = await signup(email, password, fullName);
      if (success) {
        // Se cadastro bem-sucedido, redirecionar para login
        navigate('/login', { 
          state: { message: 'Cadastro realizado! Verifique seu email para confirmar a conta.' }
        });
      }
    } catch (err) {
      setError(err.message || 'Erro ao realizar cadastro');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-vtal-primary via-vtal-secondary to-vtal-dark flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-display font-bold text-vtal-gray-800 mb-2">🚀</h1>
          <h2 className="text-2xl font-display font-bold text-vtal-gray-800">Criar Conta</h2>
          <p className="text-vtal-gray-600 mt-2">Cadastre-se para acessar o sistema</p>
        </div>

        {allowedDomains.length > 0 && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800">
              <strong>Domínios permitidos:</strong> {allowedDomains.join(', ')}
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Nome Completo
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent transition-all"
              placeholder="Seu nome completo"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent transition-all"
              placeholder="seu.email@vtal.com"
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
              placeholder="Mínimo 6 caracteres"
              required
              minLength={6}
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Confirmar Senha
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent transition-all"
              placeholder="Digite a senha novamente"
              required
              minLength={6}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-vtal-secondary to-vtal-primary hover:from-vtal-primary hover:to-vtal-dark text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-vtal-gray-200 text-center">
          <p className="text-sm text-vtal-gray-600">
            Já tem uma conta?{' '}
            <Link to="/login" className="text-vtal-secondary hover:text-vtal-primary font-medium">
              Fazer login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Signup;
