import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

function UserManagement() {
  const { hasRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, pending, approved
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get('/auth/users');
      setUsers(response.data.users || []);
    } catch (error) {
      if (error.response?.status === 404) {
        // Endpoint não existe - mostrar mensagem informativa
        console.info('Endpoint de gerenciamento de usuários não disponível no backend');
        setUsers([]);
      } else {
        console.error('Erro ao carregar usuários:', error);
        toast.error('Erro ao carregar usuários');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId, newRole) => {
    try {
      await api.put(`/auth/users/${userId}/role`, { role: newRole });
      toast.success('Role atualizada com sucesso!');
      loadUsers(); // Recarregar lista
    } catch (error) {
      console.error('Erro ao atualizar role:', error);
      toast.error(error.response?.data?.error || 'Erro ao atualizar role');
    }
  };

  const approveUser = async (userId) => {
    try {
      // Se o backend tiver endpoint de aprovação, usar ele
      // Por enquanto, vamos apenas atualizar o role para 'visualizador' como aprovação
      await api.put(`/auth/users/${userId}/role`, { role: 'visualizador' });
      toast.success('Usuário aprovado com sucesso!');
      loadUsers();
    } catch (error) {
      console.error('Erro ao aprovar usuário:', error);
      toast.error(error.response?.data?.error || 'Erro ao aprovar usuário');
    }
  };

  const rejectUser = async (userId) => {
    try {
      // Se o backend tiver endpoint de rejeição, usar ele
      // Por enquanto, vamos apenas mostrar uma mensagem
      toast.error('Funcionalidade de rejeição ainda não implementada no backend');
    } catch (error) {
      console.error('Erro ao rejeitar usuário:', error);
      toast.error('Erro ao rejeitar usuário');
    }
  };

  // Filtrar usuários
  const filteredUsers = users.filter(user => {
    // Filtro por status
    if (filter === 'pending') {
      // Usuários pendentes são aqueles sem role ou com role 'pending'
      if (user.role && user.role !== 'pending') return false;
    } else if (filter === 'approved') {
      // Usuários aprovados têm role definida
      if (!user.role || user.role === 'pending') return false;
    }

    // Filtro por busca
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return (
        user.email?.toLowerCase().includes(search) ||
        user.full_name?.toLowerCase().includes(search) ||
        user.role?.toLowerCase().includes(search)
      );
    }

    return true;
  });

  const roleOptions = [
    { value: 'visualizador', label: 'Visualizador' },
    { value: 'lider_mudanca', label: 'Líder da Mudança' },
    { value: 'administrador', label: 'Administrador' }
  ];

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'administrador':
        return 'bg-red-100 text-red-800';
      case 'lider_mudanca':
        return 'bg-blue-100 text-blue-800';
      case 'visualizador':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'administrador':
        return 'Administrador';
      case 'lider_mudanca':
        return 'Líder da Mudança';
      case 'visualizador':
        return 'Visualizador';
      default:
        return 'Pendente';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-vtal-gray-800">
          👥 Gerenciamento de Usuários
        </h1>
        <button
          onClick={loadUsers}
          className="bg-vtal-secondary hover:bg-vtal-primary text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
        >
          <span>🔄</span>
          <span>Atualizar</span>
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow-md p-4 md:p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Filtro por status */}
          <div>
            <label className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Filtrar por status
            </label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent"
            >
              <option value="all">Todos</option>
              <option value="pending">Pendentes</option>
              <option value="approved">Aprovados</option>
            </select>
          </div>

          {/* Busca */}
          <div>
            <label className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Buscar
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por email ou nome..."
              className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Lista de usuários */}
      {users.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            {filter === 'pending'
              ? 'Nenhum usuário pendente encontrado.'
              : 'Nenhum usuário encontrado. O endpoint de gerenciamento de usuários pode não estar disponível no backend.'}
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-vtal-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-vtal-gray-700">Usuário</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-vtal-gray-700">Email</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-vtal-gray-700">Role</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-vtal-gray-700">Status</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-vtal-gray-700">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-vtal-gray-200">
                {filteredUsers.map((user) => {
                  const isPending = !user.role || user.role === 'pending';
                  return (
                    <tr key={user.id} className="hover:bg-vtal-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 rounded-full bg-vtal-secondary text-white flex items-center justify-center font-bold">
                            {user.full_name?.charAt(0) || user.email?.charAt(0) || 'U'}
                          </div>
                          <div>
                            <p className="font-medium text-vtal-gray-800">
                              {user.full_name || 'Sem nome'}
                            </p>
                            <p className="text-sm text-vtal-gray-500">
                              {user.created_at ? new Date(user.created_at).toLocaleDateString('pt-BR') : '-'}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-vtal-gray-700">{user.email}</td>
                      <td className="px-4 py-3">
                        <select
                          value={user.role || 'pending'}
                          onChange={(e) => updateUserRole(user.id, e.target.value)}
                          className={`px-3 py-1 rounded-lg border border-vtal-gray-300 focus:ring-2 focus:ring-vtal-secondary focus:border-transparent ${getRoleBadgeColor(user.role || 'pending')}`}
                        >
                          <option value="pending">Pendente</option>
                          {roleOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${isPending ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                          {isPending ? '⏳ Pendente' : '✅ Aprovado'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center space-x-2">
                          {isPending && (
                            <>
                              <button
                                onClick={() => approveUser(user.id)}
                                className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                                title="Aprovar usuário"
                              >
                                ✅ Aprovar
                              </button>
                              <button
                                onClick={() => rejectUser(user.id)}
                                className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm transition-colors"
                                title="Rejeitar usuário"
                              >
                                ❌ Rejeitar
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-vtal-secondary">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-sm font-medium">Total de Usuários</p>
              <p className="text-2xl font-display font-bold text-vtal-gray-800 mt-1">{users.length}</p>
            </div>
            <div className="text-2xl">👥</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-sm font-medium">Pendentes</p>
              <p className="text-2xl font-display font-bold text-yellow-600 mt-1">
                {users.filter(u => !u.role || u.role === 'pending').length}
              </p>
            </div>
            <div className="text-2xl">⏳</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-sm font-medium">Aprovados</p>
              <p className="text-2xl font-display font-bold text-green-600 mt-1">
                {users.filter(u => u.role && u.role !== 'pending').length}
              </p>
            </div>
            <div className="text-2xl">✅</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UserManagement;
