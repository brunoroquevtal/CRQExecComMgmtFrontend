import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

const SEQUENCIAS = ['REDE', 'OPENSHIFT', 'NFS', 'SI'];

// Componentes de ícones SVG para cada CRQ
const RedeIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
  </svg>
);

const OpenShiftIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
  </svg>
);

const NFSIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
  </svg>
);

const SIIcon = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
);

const SEQUENCIAS_INFO = {
  REDE: { nome: 'REDE', icon: RedeIcon, color: 'text-green-600' },
  OPENSHIFT: { nome: 'OPENSHIFT', icon: OpenShiftIcon, color: 'text-blue-600' },
  NFS: { nome: 'NFS', icon: NFSIcon, color: 'text-orange-600' },
  SI: { nome: 'SI', icon: SIIcon, color: 'text-yellow-600' }
};

// Função para obter cor do status baseado nos novos status
const getStatusColor = (status) => {
  if (!status) return 'bg-vtal-gray-100 text-vtal-gray-600';
  const statusLower = status.toLowerCase();
  
  // N/A para milestones
  if (statusLower === 'n/a') {
    return 'bg-vtal-gray-100 text-vtal-gray-600';
  }
  // Concluído - verde claro
  else if (statusLower.includes('concluído') || statusLower.includes('concluido')) {
    return 'bg-green-100 text-green-800';
  }
  // Em execução no prazo - azul brilhante
  else if (statusLower.includes('em execução no prazo') || statusLower.includes('em execucao no prazo')) {
    return 'bg-blue-600 text-white';
  }
  // Em execução fora do prazo - vermelho
  else if (statusLower.includes('em execução fora do prazo') || statusLower.includes('em execucao fora do prazo')) {
    return 'bg-red-500 text-white';
  }
  // A Iniciar no prazo - azul claro
  else if (statusLower.includes('a iniciar no prazo')) {
    return 'bg-blue-100 text-blue-800';
  }
  // A Iniciar fora do prazo - laranja
  else if (statusLower.includes('a iniciar fora do prazo')) {
    return 'bg-orange-200 text-orange-900';
  }
  // Status desconhecido - usar cor padrão
  return 'bg-vtal-gray-100 text-vtal-gray-600';
};

// Função para formatar tempo em minutos para formato hh:mm
const formatTempo = (tempo) => {
  if (!tempo || tempo === 0) return '-';
  
  const minutos = Math.floor(Number(tempo));
  const horas = Math.floor(minutos / 60);
  const minutosRestantes = minutos % 60;
  
  return `${String(horas).padStart(2, '0')}:${String(minutosRestantes).padStart(2, '0')}`;
};

// Função para abreviar texto com tooltip
const abbreviateText = (text, maxLength = 7) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

function DataEditor() {
  const [activities, setActivities] = useState([]);
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  // Aba selecionada (CRQ)
  const [activeTab, setActiveTab] = useState('all');

  // Filtros para listagem
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(20);

  // Menu de contexto
  const [contextMenu, setContextMenu] = useState(null);
  const [contextMenuActivity, setContextMenuActivity] = useState(null);
  
  // Obter lista única de status das atividades carregadas
  const availableStatuses = React.useMemo(() => {
    const statusSet = new Set();
    activities.forEach(activity => {
      if (activity.status) {
        statusSet.add(activity.status);
      }
    });
    return Array.from(statusSet).sort();
  }, [activities]);
  
  // Calcular atividades paginadas
  const paginatedActivities = React.useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredActivities.slice(startIndex, endIndex);
  }, [filteredActivities, currentPage, itemsPerPage]);
  
  // Calcular total de páginas
  const totalPages = Math.ceil(filteredActivities.length / itemsPerPage);
  
  // Resetar para primeira página quando filtros mudarem
  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab, filterStatus, searchTerm]);

  // Estados dos modais
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);

  // Formulário de edição
  const [editForm, setEditForm] = useState({
    atividade: '',
    grupo: '',
    inicio: '',
    fim: '',
    status: 'Planejado',
    horario_inicio_real: '',
    horario_fim_real: '',
    observacoes: '',
    is_milestone: false
  });

  useEffect(() => {
    loadActivities();
  }, []);

  useEffect(() => {
    filterActivities();
  }, [activities, activeTab, filterStatus, searchTerm]);

  const loadActivities = async () => {
    try {
      const response = await api.get('/activities');
      setActivities(response.data.activities || []);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar atividades:', error);
      
      // Mensagem de erro mais detalhada
      let errorMessage = 'Erro ao carregar atividades';
      if (error.response) {
        errorMessage = `Erro ${error.response.status}: ${error.response.data?.error || error.message}`;
      } else if (error.request) {
        errorMessage = 'Não foi possível conectar ao backend. Verifique se a API está configurada corretamente.';
        console.error('URL da API:', import.meta.env.VITE_API_URL || '/api (padrão)');
      } else {
        errorMessage = `Erro: ${error.message}`;
      }
      
      toast.error(errorMessage);
      setLoading(false);
    }
  };

  const filterActivities = () => {
    let filtered = [...activities];

    // Filtrar por CRQ (aba selecionada)
    if (activeTab !== 'all') {
      filtered = filtered.filter(a => a.sequencia === activeTab);
    }

    // Filtrar por status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(a => a.status === filterStatus);
    }

    // Filtrar por busca
    if (searchTerm) {
      const lowerTerm = searchTerm.toLowerCase();
      filtered = filtered.filter(a =>
        a.atividade.toLowerCase().includes(lowerTerm) ||
        (a.grupo && a.grupo.toLowerCase().includes(lowerTerm))
      );
    }

    setFilteredActivities(filtered);
  };

  // Abrir modal de edição
  const openEditModal = (activity) => {
    setSelectedActivity(activity);
    setEditForm({
      atividade: activity.atividade || '',
      grupo: activity.grupo || '',
      inicio: activity.inicio ? format(new Date(activity.inicio), 'yyyy-MM-dd\'T\'HH:mm') : '',
      fim: activity.fim ? format(new Date(activity.fim), 'yyyy-MM-dd\'T\'HH:mm') : '',
      status: activity.status || 'Planejado',
      horario_inicio_real: activity.horario_inicio_real ? format(new Date(activity.horario_inicio_real), 'yyyy-MM-dd\'T\'HH:mm') : '',
      horario_fim_real: activity.horario_fim_real ? format(new Date(activity.horario_fim_real), 'yyyy-MM-dd\'T\'HH:mm') : '',
      observacoes: activity.observacoes || '',
      is_milestone: activity.is_milestone || false
    });
    setShowEditModal(true);
  };

  // Abrir modal de exclusão
  const openDeleteModal = (activity) => {
    setSelectedActivity(activity);
    setShowDeleteModal(true);
  };

  // Abrir modal de detalhes
  const openDetailsModal = (activity) => {
    setSelectedActivity(activity);
    setShowDetailsModal(true);
  };

  // Fechar modais
  const closeModals = () => {
    setShowEditModal(false);
    setShowDeleteModal(false);
    setShowDetailsModal(false);
    setSelectedActivity(null);
  };

  // Menu de contexto
  const handleContextMenu = (e, activity) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY
    });
    setContextMenuActivity(activity);
  };

  const closeContextMenu = () => {
    setContextMenu(null);
    setContextMenuActivity(null);
  };

  const handleContextMenuAction = (action, activity) => {
    closeContextMenu();
    if (action === 'details') {
      openDetailsModal(activity);
    } else if (action === 'edit') {
      openEditModal(activity);
    } else if (action === 'delete') {
      openDeleteModal(activity);
    }
  };

  // Fechar menu de contexto ao clicar fora
  useEffect(() => {
    if (!contextMenu) return;

    const handleClickOutside = () => {
      setContextMenu(null);
      setContextMenuActivity(null);
    };

    // Adicionar listener após um pequeno delay para não fechar imediatamente
    const timeoutId = setTimeout(() => {
      document.addEventListener('click', handleClickOutside);
    }, 0);

    return () => {
      clearTimeout(timeoutId);
      document.removeEventListener('click', handleClickOutside);
    };
  }, [contextMenu]);

  // Salvar edição
  const handleEdit = async (e) => {
    e.preventDefault();

    if (!selectedActivity) return;

    try {
      // Enviar apenas os campos editáveis
      await api.put('/activity', {
        seq: selectedActivity.seq,
        sequencia: selectedActivity.sequencia,
        excel_data_id: selectedActivity.excel_data_id || null,
        // Manter os valores originais dos campos não editáveis
        atividade: selectedActivity.atividade,
        grupo: selectedActivity.grupo,
        status: selectedActivity.status,
        inicio: selectedActivity.inicio,
        fim: selectedActivity.fim,
        // Campos editáveis do formulário
        is_milestone: editForm.is_milestone,
        horario_inicio_real: editForm.horario_inicio_real || null,
        horario_fim_real: editForm.horario_fim_real || null,
        observacoes: editForm.observacoes || ''
      });
      toast.success('Atividade atualizada com sucesso!');
      closeModals();
      loadActivities();
    } catch (error) {
      console.error('Erro ao atualizar:', error);
      toast.error(error.response?.data?.error || 'Erro ao atualizar atividade');
    }
  };

  // Confirmar exclusão
  const handleDelete = async () => {
    if (!selectedActivity) return;

    try {
      await api.delete('/activity', {
        data: {
          seq: selectedActivity.seq,
          sequencia: selectedActivity.sequencia,
          excel_data_id: selectedActivity.excel_data_id || null
        }
      });
      toast.success('Atividade excluída com sucesso!');
      closeModals();
      loadActivities();
    } catch (error) {
      console.error('Erro ao excluir:', error);
      toast.error(error.response?.data?.error || 'Erro ao excluir atividade');
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-display font-bold text-vtal-gray-800">✏️ Editor de Dados</h1>
        <div className="bg-vtal-light border border-vtal-secondary/30 rounded-lg px-4 py-2">
          <p className="text-sm text-vtal-gray-700">
            <span className="font-semibold">ℹ️</span> As atividades são criadas automaticamente via script de sincronização
          </p>
        </div>
      </div>

      {/* Abas por CRQ */}
      <div className="bg-white rounded-xl shadow-md overflow-x-auto">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-4 md:space-x-8 px-3 md:px-6 min-w-max">
            <button
              onClick={() => setActiveTab('all')}
              className={`py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm transition-colors whitespace-nowrap ${
                activeTab === 'all'
                  ? 'border-vtal-secondary text-vtal-secondary'
                  : 'border-transparent text-vtal-gray-600 hover:text-vtal-gray-800 hover:border-vtal-gray-300'
              }`}
            >
              📋 Todos
            </button>
            {SEQUENCIAS.map(seq => {
              const Icon = SEQUENCIAS_INFO[seq].icon;
              return (
                <button
                  key={seq}
                  onClick={() => setActiveTab(seq)}
                  className={`py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm transition-colors flex items-center space-x-1 md:space-x-2 whitespace-nowrap ${
                    activeTab === seq
                      ? 'border-vtal-secondary text-vtal-secondary'
                      : 'border-transparent text-vtal-gray-600 hover:text-vtal-gray-800 hover:border-vtal-gray-300'
                  }`}
                >
                  <Icon className={`w-4 h-4 md:w-5 md:h-5 ${activeTab === seq ? SEQUENCIAS_INFO[seq].color : ''}`} />
                  <span className="hidden sm:inline">{SEQUENCIAS_INFO[seq].nome}</span>
                  <span className="sm:hidden">{SEQUENCIAS_INFO[seq].nome.substring(0, 3)}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Filtrar por Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary"
            >
              <option value="all">Todos</option>
              {availableStatuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Buscar</label>
            <input
              type="text"
              placeholder="Buscar atividade, grupo..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary"
            />
          </div>
        </div>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-vtal-gray-200">
            <thead className="bg-vtal-gray-50">
              <tr>
                {activeTab === 'all' && (
                  <th rowSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase align-top">CRQ</th>
                )}
                <th rowSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase align-top">Seq</th>
                <th rowSpan={2} className="px-4 py-2 text-left text-[10px] font-bold text-vtal-gray-600 uppercase w-1/3 align-top">Atividade</th>
                <th rowSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase align-top">Grupo</th>
                <th rowSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase align-top">Tempo</th>
                <th rowSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase align-top">Status</th>
                <th colSpan={2} className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase border-x border-vtal-gray-300">Horário</th>
              </tr>
              <tr>
                <th className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase border-l border-vtal-gray-300 align-middle">Início</th>
                <th className="px-3 py-2 text-center text-[10px] font-bold text-vtal-gray-600 uppercase border-r border-vtal-gray-300 align-middle">Fim</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-vtal-gray-200">
              {paginatedActivities.map((activity, idx) => (
                <tr 
                  key={`${activity.seq}-${activity.sequencia}-${idx}`} 
                  className="hover:bg-vtal-gray-50 cursor-context-menu"
                  onContextMenu={(e) => handleContextMenu(e, activity)}
                >
                  {activeTab === 'all' && (
                    <td className="px-3 py-2 whitespace-nowrap text-[10px] font-normal text-vtal-gray-900 text-center align-middle">{activity.sequencia}</td>
                  )}
                  <td className="px-3 py-2 whitespace-nowrap text-[10px] font-normal text-vtal-gray-900 text-center align-middle">{activity.seq}</td>
                  <td className="px-4 py-2 text-[10px] font-normal text-vtal-gray-700 text-left align-middle">{activity.atividade}</td>
                  <td 
                    className="px-3 py-2 text-[10px] font-normal text-vtal-gray-500 text-center align-middle cursor-help"
                    title={activity.grupo || '-'}
                  >
                    {activity.grupo ? abbreviateText(activity.grupo) : '-'}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-[10px] font-normal text-vtal-gray-600 text-center align-middle">
                    {formatTempo(activity.tempo)}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap text-center align-middle">
                    <span className={`px-1.5 py-0.5 text-[10px] font-normal rounded-full ${getStatusColor(activity.status)}`}>
                      {activity.is_milestone ? 'N/A' : (activity.status || '-')}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-[10px] font-normal text-vtal-gray-600 text-center align-middle">
                    <div className="space-y-0.5">
                      {activity.horario_inicio_real ? (
                        <div>
                          <span className="font-normal text-vtal-secondary text-[10px]">Real:</span>{' '}
                          <span className="font-normal text-[10px]">{format(new Date(activity.horario_inicio_real), 'dd/MM/yyyy HH:mm')}</span>
                        </div>
                      ) : (
                        <div>
                          <span className="font-normal text-vtal-secondary text-[10px]">Real:</span>{' '}
                          <span className="font-normal text-vtal-gray-400 text-[10px]">-</span>
                        </div>
                      )}
                      {activity.inicio ? (
                        <div>
                          <span className="font-normal text-vtal-gray-600 text-[10px]">Plan:</span>{' '}
                          <span className="font-normal text-[10px]">{format(new Date(activity.inicio), 'dd/MM/yyyy HH:mm')}</span>
                        </div>
                      ) : (
                        <div>
                          <span className="font-normal text-vtal-gray-600 text-[10px]">Plan:</span>{' '}
                          <span className="font-normal text-vtal-gray-400 text-[10px]">-</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-2 text-[10px] font-normal text-vtal-gray-600 text-center align-middle">
                    <div className="space-y-0.5">
                      {activity.horario_fim_real ? (
                        <div>
                          <span className="font-normal text-vtal-secondary text-[10px]">Real:</span>{' '}
                          <span className="font-normal text-[10px]">{format(new Date(activity.horario_fim_real), 'dd/MM/yyyy HH:mm')}</span>
                        </div>
                      ) : (
                        <div>
                          <span className="font-normal text-vtal-secondary text-[10px]">Real:</span>{' '}
                          <span className="font-normal text-vtal-gray-400 text-[10px]">-</span>
                        </div>
                      )}
                      {activity.fim ? (
                        <div>
                          <span className="font-normal text-vtal-gray-600 text-[10px]">Plan:</span>{' '}
                          <span className="font-normal text-[10px]">{format(new Date(activity.fim), 'dd/MM/yyyy HH:mm')}</span>
                        </div>
                      ) : (
                        <div>
                          <span className="font-normal text-vtal-gray-600 text-[10px]">Plan:</span>{' '}
                          <span className="font-normal text-vtal-gray-400 text-[10px]">-</span>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredActivities.length === 0 && (
          <div className="text-center py-12 text-vtal-gray-500">
            Nenhuma atividade encontrada com os filtros aplicados.
          </div>
        )}

        {/* Paginação */}
        {filteredActivities.length > 0 && (
          <div className="px-4 py-3 bg-vtal-gray-50 border-t border-vtal-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <p className="text-xs text-vtal-gray-600">
                Mostrando <strong>{(currentPage - 1) * itemsPerPage + 1}</strong> a{' '}
                <strong>{Math.min(currentPage * itemsPerPage, filteredActivities.length)}</strong> de{' '}
                <strong>{filteredActivities.length}</strong> atividades
              </p>
              <div className="flex items-center space-x-2">
                <label className="text-xs text-vtal-gray-600">Itens por página:</label>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="px-2 py-1 text-xs border border-vtal-gray-300 rounded focus:ring-2 focus:ring-vtal-secondary"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                </select>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 text-xs bg-white border border-vtal-gray-300 rounded hover:bg-vtal-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Anterior
              </button>
              
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-2 py-1 text-xs rounded transition-colors ${
                        currentPage === pageNum
                          ? 'bg-vtal-secondary text-white'
                          : 'bg-white border border-vtal-gray-300 text-vtal-gray-700 hover:bg-vtal-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 text-xs bg-white border border-vtal-gray-300 rounded hover:bg-vtal-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Próximo
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal: Ver Detalhes */}
      {showDetailsModal && selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-vtal-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-display font-semibold text-vtal-gray-800">👁️ Detalhes da Atividade</h2>
                <button
                  onClick={closeModals}
                  className="text-vtal-gray-400 hover:text-vtal-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">CRQ</label>
                  <p className="text-vtal-gray-900">{selectedActivity.sequencia}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Seq</label>
                  <p className="text-vtal-gray-900">{selectedActivity.seq}</p>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Atividade</label>
                  <p className="text-vtal-gray-900">{selectedActivity.atividade}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Grupo</label>
                  <p className="text-vtal-gray-900">{selectedActivity.grupo || '-'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Tempo</label>
                  <p className="text-vtal-gray-900">{formatTempo(selectedActivity.tempo)}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Status</label>
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(selectedActivity.status)}`}>
                    {selectedActivity.is_milestone ? 'N/A' : (selectedActivity.status || '-')}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Início Planejado</label>
                  <p className="text-vtal-gray-900">
                    {selectedActivity.inicio ? format(new Date(selectedActivity.inicio), 'dd/MM/yyyy HH:mm') : '-'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Fim Planejado</label>
                  <p className="text-vtal-gray-900">
                    {selectedActivity.fim ? format(new Date(selectedActivity.fim), 'dd/MM/yyyy HH:mm') : '-'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Horário Início Real</label>
                  <p className="text-vtal-gray-900">
                    {selectedActivity.horario_inicio_real ? format(new Date(selectedActivity.horario_inicio_real), 'dd/MM/yyyy HH:mm') : '-'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Horário Fim Real</label>
                  <p className="text-vtal-gray-900">
                    {selectedActivity.horario_fim_real ? format(new Date(selectedActivity.horario_fim_real), 'dd/MM/yyyy HH:mm') : '-'}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Atraso (minutos)</label>
                  <p className="text-vtal-gray-900">{selectedActivity.atraso_minutos || 0}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">É Milestone?</label>
                  <p className="text-vtal-gray-900">{selectedActivity.is_milestone ? 'Sim' : 'Não'}</p>
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-1">Observações</label>
                  <p className="text-vtal-gray-900 whitespace-pre-wrap">{selectedActivity.observacoes || '-'}</p>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-vtal-gray-200 flex justify-end">
              <button
                onClick={closeModals}
                className="px-6 py-2 bg-vtal-gray-600 text-white rounded-lg hover:bg-vtal-gray-700 focus:ring-2 focus:ring-vtal-gray-500"
              >
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Editar */}
      {showEditModal && selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-vtal-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-display font-semibold text-vtal-gray-800">✏️ Editar Atividade</h2>
                <button
                  onClick={closeModals}
                  className="text-vtal-gray-400 hover:text-vtal-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>
            <form onSubmit={handleEdit} className="p-6">
              <div className="mb-4 bg-vtal-light border border-vtal-secondary/30 rounded-lg p-3">
                <p className="text-sm text-vtal-gray-700">
                  <span className="font-semibold">ℹ️</span> Apenas os campos de Horário Início Real, Horário Fim Real e Observações podem ser alterados.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Atividade</label>
                  <input
                    type="text"
                    value={editForm.atividade}
                    readOnly
                    disabled
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg bg-vtal-gray-100 text-vtal-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Grupo</label>
                  <input
                    type="text"
                    value={editForm.grupo}
                    readOnly
                    disabled
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg bg-vtal-gray-100 text-vtal-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Status</label>
                  <input
                    type="text"
                    value={editForm.status}
                    readOnly
                    disabled
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg bg-vtal-gray-100 text-vtal-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Início Planejado</label>
                  <input
                    type="datetime-local"
                    value={editForm.inicio}
                    readOnly
                    disabled
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg bg-vtal-gray-100 text-vtal-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Fim Planejado</label>
                  <input
                    type="datetime-local"
                    value={editForm.fim}
                    readOnly
                    disabled
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg bg-vtal-gray-100 text-vtal-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">
                    Horário Início Real <span className="text-vtal-secondary">*</span>
                  </label>
                  <input
                    type="datetime-local"
                    value={editForm.horario_inicio_real}
                    onChange={(e) => setEditForm({ ...editForm, horario_inicio_real: e.target.value })}
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-vtal-secondary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">
                    Horário Fim Real <span className="text-vtal-secondary">*</span>
                  </label>
                  <input
                    type="datetime-local"
                    value={editForm.horario_fim_real}
                    onChange={(e) => setEditForm({ ...editForm, horario_fim_real: e.target.value })}
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-vtal-secondary"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-vtal-gray-700 mb-2">Observações</label>
                  <textarea
                    value={editForm.observacoes}
                    onChange={(e) => setEditForm({ ...editForm, observacoes: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-vtal-secondary"
                    placeholder="Digite suas observações aqui..."
                  />
                </div>

                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editForm.is_milestone}
                      onChange={(e) => setEditForm({ ...editForm, is_milestone: e.target.checked })}
                      className="mr-2 cursor-pointer"
                    />
                    <span className="text-sm font-medium text-vtal-gray-700">É Milestone?</span>
                  </label>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={closeModals}
                  className="px-6 py-2 bg-vtal-gray-600 text-white rounded-lg hover:bg-vtal-gray-700 focus:ring-2 focus:ring-vtal-gray-500"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-vtal-secondary text-white rounded-lg hover:bg-vtal-primary focus:ring-2 focus:ring-vtal-secondary"
                >
                  💾 Salvar Alterações
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Excluir */}
      {showDeleteModal && selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-gray-800">🗑️ Excluir Atividade</h2>
                <button
                  onClick={closeModals}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <p className="text-yellow-800 font-semibold">⚠️ Atenção: Esta ação é irreversível!</p>
              </div>
              <p className="text-gray-700 mb-4">Tem certeza que deseja excluir a seguinte atividade?</p>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                <ul className="text-sm text-gray-600 space-y-1">
                  <li><strong>Seq:</strong> {selectedActivity.seq}</li>
                  <li><strong>CRQ:</strong> {selectedActivity.sequencia}</li>
                  <li><strong>Atividade:</strong> {selectedActivity.atividade}</li>
                  <li><strong>Status:</strong> {selectedActivity.is_milestone ? 'N/A' : (selectedActivity.status || '-')}</li>
                </ul>
              </div>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={closeModals}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500"
              >
                Cancelar
              </button>
              <button
                onClick={handleDelete}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500"
              >
                🗑️ Excluir
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Menu de Contexto */}
      {contextMenu && contextMenuActivity && (
        <div
          className="fixed z-50 bg-white rounded-lg shadow-xl border border-vtal-gray-200 py-1 min-w-[180px]"
          style={{
            left: `${contextMenu.x}px`,
            top: `${contextMenu.y}px`,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => handleContextMenuAction('details', contextMenuActivity)}
            className="w-full px-4 py-2 text-left text-sm text-vtal-gray-700 hover:bg-vtal-gray-100 flex items-center space-x-2 transition-colors"
          >
            <span>👁️</span>
            <span>Ver Detalhes</span>
          </button>
          <button
            onClick={() => handleContextMenuAction('edit', contextMenuActivity)}
            className="w-full px-4 py-2 text-left text-sm text-vtal-gray-700 hover:bg-yellow-50 flex items-center space-x-2 transition-colors"
          >
            <span>✏️</span>
            <span>Alterar</span>
          </button>
          <button
            onClick={() => handleContextMenuAction('delete', contextMenuActivity)}
            className="w-full px-4 py-2 text-left text-sm text-vtal-gray-700 hover:bg-red-50 flex items-center space-x-2 transition-colors"
          >
            <span>🗑️</span>
            <span>Excluir</span>
          </button>
        </div>
      )}
    </div>
  );
}

export default DataEditor;
