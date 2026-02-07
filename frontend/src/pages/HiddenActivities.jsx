import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';

function HiddenActivities() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSequencia, setFilterSequencia] = useState('all');
  const [updatingIds, setUpdatingIds] = useState(new Set());

  useEffect(() => {
    loadHiddenActivities();
  }, []);

  const loadHiddenActivities = async () => {
    setLoading(true);
    try {
      const response = await api.get('/hidden-activities');
      setActivities(response.data.activities || []);
    } catch (error) {
      if (error.response?.status === 404) {
        console.info('Endpoint de atividades ocultas não disponível no backend');
        setActivities([]);
      } else {
        console.error('Erro ao carregar atividades ocultas:', error);
        toast.error('Erro ao carregar atividades ocultas');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateVisibility = async (activityId, makeVisible) => {
    setUpdatingIds(prev => new Set(prev).add(activityId));
    try {
      await api.put(`/activity/${activityId}/visibility`, { is_visible: makeVisible });
      toast.success(`Atividade ${makeVisible ? 'tornada visível' : 'ocultada'} com sucesso!`);
      loadHiddenActivities(); // Recarregar lista
    } catch (error) {
      console.error('Erro ao atualizar visibilidade:', error);
      toast.error(error.response?.data?.error || 'Erro ao atualizar visibilidade');
    } finally {
      setUpdatingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(activityId);
        return newSet;
      });
    }
  };

  // Obter sequências únicas para filtro
  const sequencias = [...new Set(activities.map(a => a.sequencia))].sort();

  // Filtrar atividades
  const filteredActivities = activities.filter(activity => {
    const matchesSearch = searchTerm === '' ||
      activity.atividade?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.grupo?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      String(activity.seq).includes(searchTerm);
    
    const matchesSequencia = filterSequencia === 'all' || activity.sequencia === filterSequencia;
    
    return matchesSearch && matchesSequencia;
  });

  // Formatar data para exibição
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    try {
      const date = new Date(dateString);
      return date.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return dateString;
    }
  };

  // Formatar tempo (minutos para horas:minutos)
  const formatTime = (minutes) => {
    if (!minutes || minutes === 0) return '-';
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    return `${hours}h ${mins}min`;
  };

  return (
    <div className="container mx-auto p-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-vtal-blue mb-2">Atividades Ocultas</h1>
        <p className="text-gray-600">
          Registros importados do Excel que não atendem aos critérios de exibição. 
          Você pode torná-los visíveis para que apareçam nos dashboards e relatórios.
        </p>
      </div>

      {/* Filtros e busca */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 space-y-4 md:space-y-0 md:space-x-4">
        <div className="flex space-x-2 w-full md:w-auto">
          <select
            value={filterSequencia}
            onChange={(e) => setFilterSequencia(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium bg-white"
          >
            <option value="all">Todas as Sequências</option>
            {sequencias.map(seq => (
              <option key={seq} value={seq}>{seq}</option>
            ))}
          </select>
        </div>
        <input
          type="text"
          placeholder="Buscar por atividade, grupo ou seq..."
          className="p-2 border border-gray-300 rounded-md w-full md:w-auto flex-1 md:flex-initial"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Estatísticas */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-blue-800 font-medium">Total de atividades ocultas</p>
            <p className="text-2xl font-bold text-blue-900">{activities.length}</p>
          </div>
          <div>
            <p className="text-sm text-blue-800 font-medium">Filtradas</p>
            <p className="text-2xl font-bold text-blue-900">{filteredActivities.length}</p>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary"></div>
        </div>
      ) : filteredActivities.length === 0 ? (
        <div className="bg-white shadow-md rounded-lg p-8 text-center">
          <p className="text-gray-500 text-lg">
            {activities.length === 0 
              ? 'Nenhuma atividade oculta encontrada.' 
              : 'Nenhuma atividade oculta corresponde aos filtros aplicados.'}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Seq
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sequência
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Atividade
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Grupo
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Início
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fim
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tempo
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredActivities.map((activity) => (
                  <tr key={activity.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {activity.seq || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {activity.sequencia}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {activity.atividade || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.grupo || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(activity.inicio)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(activity.fim)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatTime(activity.tempo)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => updateVisibility(activity.id, true)}
                        disabled={updatingIds.has(activity.id)}
                        className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                      >
                        {updatingIds.has(activity.id) ? 'Atualizando...' : 'Tornar Visível'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default HiddenActivities;
