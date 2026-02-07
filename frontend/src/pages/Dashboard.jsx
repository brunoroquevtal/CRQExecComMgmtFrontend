import React, { useState, useEffect, useMemo } from 'react';
import api from '../utils/api';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';

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

function Dashboard() {
  const [statistics, setStatistics] = useState(null);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, activitiesRes] = await Promise.all([
        api.get('/statistics'),
        api.get('/activities')
      ]);
      setStatistics(statsRes.data);
      setActivities(activitiesRes.data.activities || []);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      
      // Mensagem de erro mais detalhada
      let errorMessage = 'Erro ao carregar dados do dashboard';
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

  // Filtrar dados baseado na aba selecionada
  const getFilteredData = () => {
    if (!statistics) return null;

    if (activeTab === 'all') {
      return statistics;
    }

    // Filtrar por CRQ selecionado
    const filteredStats = {
      geral: {
        total: 0,
        concluidas: 0,
        em_execucao_no_prazo: 0,
        em_execucao_fora_prazo: 0,
        a_iniciar_no_prazo: 0,
        a_iniciar_fora_prazo: 0
      },
      por_sequencia: {}
    };

    if (statistics.por_sequencia[activeTab]) {
      const seqStats = statistics.por_sequencia[activeTab];
      filteredStats.geral = { ...seqStats };
      filteredStats.por_sequencia[activeTab] = seqStats;
    }

    return filteredStats;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary"></div>
      </div>
    );
  }

  const filteredStats = getFilteredData();

  if (!filteredStats || !statistics) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <p className="text-yellow-800">Nenhum dado disponível. Faça upload de um arquivo Excel.</p>
      </div>
    );
  }

  const { geral, por_sequencia } = filteredStats;

  // Garantir que geral existe e tem todas as propriedades
  const geralSafe = geral || {
    total: 0,
    concluidas: 0,
    em_execucao_no_prazo: 0,
    em_execucao_fora_prazo: 0,
    a_iniciar_no_prazo: 0,
    a_iniciar_fora_prazo: 0
  };

  // Dados para gráfico de pizza (status)
  const statusData = [
    { name: 'Concluídas', value: geralSafe.concluidas || 0, color: '#28a745' },
    { name: 'Em Execução no Prazo', value: geralSafe.em_execucao_no_prazo || 0, color: '#3B82F6' },
    { name: 'Em Execução Fora do Prazo', value: geralSafe.em_execucao_fora_prazo || 0, color: '#EF4444' },
    { name: 'A Iniciar no Prazo', value: geralSafe.a_iniciar_no_prazo || 0, color: '#DBEAFE' },
    { name: 'A Iniciar Fora do Prazo', value: geralSafe.a_iniciar_fora_prazo || 0, color: '#FED7AA' }
  ].filter(item => item.value > 0);

  // Dados para gráfico de barras (por sequência)
  const sequenciaData = Object.entries(por_sequencia || {}).map(([seq, stats]) => {
    // Garantir que stats existe
    const statsSafe = stats || {
      concluidas: 0,
      em_execucao_no_prazo: 0,
      em_execucao_fora_prazo: 0,
      a_iniciar_no_prazo: 0,
      a_iniciar_fora_prazo: 0
    };
    
    return {
      sequencia: seq,
      concluidas: statsSafe.concluidas || 0,
      em_execucao_no_prazo: statsSafe.em_execucao_no_prazo || 0,
      em_execucao_fora_prazo: statsSafe.em_execucao_fora_prazo || 0,
      a_iniciar_no_prazo: statsSafe.a_iniciar_no_prazo || 0,
      a_iniciar_fora_prazo: statsSafe.a_iniciar_fora_prazo || 0
    };
  });

  // Filtrar atividades por status e CRQ
  const getFilteredActivities = (statusFilter) => {
    let filtered = activities.filter(activity => {
      // Excluir milestones
      if (activity.is_milestone) return false;
      
      // Filtrar por status - verificar correspondência exata ou parcial
      const statusLower = (activity.status || '').toLowerCase();
      const filterLower = statusFilter.toLowerCase();
      
      // Verificar correspondência exata ou se o status contém o filtro
      const matchesStatus = statusLower === filterLower || 
                          statusLower.includes(filterLower) ||
                          filterLower.includes(statusLower);
      
      if (!matchesStatus) return false;
      
      // Filtrar por CRQ se uma aba específica estiver selecionada
      if (activeTab !== 'all') {
        return activity.sequencia === activeTab;
      }
      
      return true;
    });
    
    return filtered;
  };

  // Atividades por categoria
  const atividadesEmExecucaoNoPrazo = getFilteredActivities('em execução no prazo');
  const atividadesEmExecucaoForaPrazo = getFilteredActivities('em execução fora do prazo');
  const atividadesAIniciarNoPrazo = getFilteredActivities('a iniciar no prazo');
  const atividadesAIniciarForaPrazo = getFilteredActivities('a iniciar fora do prazo');

  // Função para parsear data
  const parseDate = (dateValue) => {
    if (!dateValue) return null;
    if (dateValue instanceof Date && !isNaN(dateValue.getTime())) {
      return dateValue;
    }
    if (typeof dateValue === 'string') {
      try {
        const date = new Date(dateValue);
        if (!isNaN(date.getTime())) {
          return date;
        }
      } catch (e) {
        return null;
      }
    }
    return null;
  };

  // Filtrar atividades "Em Atraso"
  // Inclui: 
  // 1. Em execução fora do prazo
  // 2. A Iniciar fora do prazo
  // 3. Ainda não iniciadas quando horário atual > início planejado (mesmo que status não indique atraso)
  const atividadesEmAtraso = activities.filter(activity => {
    // Excluir milestones
    if (activity.is_milestone) return false;
    
    // Filtrar por CRQ se uma aba específica estiver selecionada
    if (activeTab !== 'all' && activity.sequencia !== activeTab) {
      return false;
    }

    const statusLower = (activity.status || '').toLowerCase();
    const now = new Date();
    
    // 1. Em execução fora do prazo
    if (statusLower.includes('em execução fora do prazo') || statusLower.includes('em execucao fora do prazo')) {
      return true;
    }
    
    // 2. A Iniciar fora do prazo
    if (statusLower.includes('a iniciar fora do prazo')) {
      return true;
    }
    
    // 3. Ainda não iniciadas (horário atual > início planejado)
    const inicioPlanejado = parseDate(activity.inicio);
    if (inicioPlanejado && now > inicioPlanejado) {
      // Verificar se não tem horário de início real (não foi iniciada)
      const horarioInicioReal = parseDate(activity.horario_inicio_real);
      if (!horarioInicioReal) {
        // Não foi iniciada e já passou do horário planejado
        return true;
      }
    }
    
    return false;
  });

  // Filtrar atividades "Em Andamento"
  // Inclui: Em execução no prazo
  const atividadesEmAndamento = getFilteredActivities('em execução no prazo');

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

  // Componente para renderizar lista de atividades com filtro e ordenação
  const ActivityList = ({ activities, title, icon, borderColor, bgColor }) => {
    const [searchText, setSearchText] = useState('');
    const [filterSequencia, setFilterSequencia] = useState('all');
    const [sortBy, setSortBy] = useState('seq'); // seq, sequencia, inicio, fim, status, atividade
    const [sortOrder, setSortOrder] = useState('asc'); // asc, desc

    // Filtrar e ordenar atividades
    const filteredAndSortedActivities = useMemo(() => {
      let filtered = [...activities];

      // Filtro por texto (busca em atividade, grupo, sequencia)
      if (searchText.trim()) {
        const searchLower = searchText.toLowerCase();
        filtered = filtered.filter(activity => {
          const atividade = (activity.atividade || '').toLowerCase();
          const grupo = (activity.grupo || '').toLowerCase();
          const sequencia = (activity.sequencia || '').toLowerCase();
          const seq = String(activity.seq || '').toLowerCase();
          return atividade.includes(searchLower) || 
                 grupo.includes(searchLower) || 
                 sequencia.includes(searchLower) ||
                 seq.includes(searchLower);
        });
      }

      // Filtro por sequencia (CRQ)
      if (filterSequencia !== 'all') {
        filtered = filtered.filter(activity => activity.sequencia === filterSequencia);
      }

      // Ordenação
      filtered.sort((a, b) => {
        let aValue, bValue;

        switch (sortBy) {
          case 'seq':
            aValue = a.seq || 0;
            bValue = b.seq || 0;
            break;
          case 'sequencia':
            aValue = (a.sequencia || '').toLowerCase();
            bValue = (b.sequencia || '').toLowerCase();
            break;
          case 'inicio':
            aValue = parseDate(a.inicio)?.getTime() || 0;
            bValue = parseDate(b.inicio)?.getTime() || 0;
            break;
          case 'fim':
            aValue = parseDate(a.fim)?.getTime() || 0;
            bValue = parseDate(b.fim)?.getTime() || 0;
            break;
          case 'status':
            aValue = (a.status || '').toLowerCase();
            bValue = (b.status || '').toLowerCase();
            break;
          case 'atividade':
            aValue = (a.atividade || '').toLowerCase();
            bValue = (b.atividade || '').toLowerCase();
            break;
          default:
            aValue = a.seq || 0;
            bValue = b.seq || 0;
        }

        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
        } else {
          if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
          if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
          return 0;
        }
      });

      return filtered;
    }, [activities, searchText, filterSequencia, sortBy, sortOrder]);

    if (activities.length === 0) {
      return (
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className={`text-lg font-display font-semibold text-vtal-gray-800 mb-4 flex items-center gap-2 ${borderColor}`}>
            <span>{icon}</span>
            <span>{title}</span>
            <span className="text-sm font-normal text-gray-500">({activities.length})</span>
          </h3>
          <p className="text-gray-500 text-sm">Nenhuma atividade encontrada</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-xl shadow-md p-6">
        <h3 className={`text-lg font-display font-semibold text-vtal-gray-800 mb-4 flex items-center gap-2 border-b-2 pb-2 ${borderColor}`}>
          <span>{icon}</span>
          <span>{title}</span>
          <span className="text-sm font-normal text-gray-500">
            ({filteredAndSortedActivities.length} de {activities.length})
          </span>
        </h3>

        {/* Controles de Filtro e Ordenação */}
        <div className="mb-4 space-y-3">
          {/* Campo de busca */}
          <div className="relative">
            <input
              type="text"
              placeholder="🔍 Buscar por atividade, grupo, CRQ ou seq..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent text-sm"
            />
            {searchText && (
              <button
                onClick={() => setSearchText('')}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            )}
          </div>

          {/* Filtros e Ordenação */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {/* Filtro por CRQ */}
            <div>
              <select
                value={filterSequencia}
                onChange={(e) => setFilterSequencia(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent text-sm"
              >
                <option value="all">Todos os CRQs</option>
                {SEQUENCIAS.map(seq => (
                  <option key={seq} value={seq}>{SEQUENCIAS_INFO[seq].nome}</option>
                ))}
              </select>
            </div>

            {/* Ordenação */}
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent text-sm"
              >
                <option value="seq">Seq</option>
                <option value="sequencia">CRQ</option>
                <option value="atividade">Atividade</option>
                <option value="inicio">Início Planejado</option>
                <option value="fim">Fim Planejado</option>
                <option value="status">Status</option>
              </select>
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-vtal-secondary focus:border-transparent text-sm"
                title={sortOrder === 'asc' ? 'Crescente' : 'Decrescente'}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>

        {filteredAndSortedActivities.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">
            Nenhuma atividade encontrada com os filtros aplicados
          </p>
        ) : (
          <div className="max-h-96 overflow-y-auto">
            <div className="space-y-2">
              {filteredAndSortedActivities.map((activity, index) => {
                const SequenciaIcon = activity.sequencia ? SEQUENCIAS_INFO[activity.sequencia]?.icon : null;
                const sequenciaColor = activity.sequencia ? SEQUENCIAS_INFO[activity.sequencia]?.color : '';
                const statusColor = getStatusColor(activity.status);
                
                return (
                  <div
                    key={`${activity.sequencia}-${activity.seq}-${index}`}
                    className={`p-3 rounded-lg border-l-4 ${bgColor} hover:shadow-md transition-shadow`}
                  >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        {SequenciaIcon && (
                          <SequenciaIcon className={`w-4 h-4 flex-shrink-0 ${sequenciaColor}`} />
                        )}
                        <span className="text-xs font-semibold text-vtal-gray-600 uppercase">
                          {activity.sequencia || 'N/A'}
                        </span>
                        <span className="text-xs text-vtal-gray-500">#{activity.seq || 'N/A'}</span>
                      </div>
                      <p className="text-sm font-medium text-vtal-gray-800 truncate">
                        {activity.atividade || activity.grupo || 'Sem descrição'}
                      </p>
                      {activity.grupo && activity.atividade && (
                        <p className="text-xs text-vtal-gray-500 mt-1 truncate">
                          {activity.grupo}
                        </p>
                      )}
                      <div className="flex items-center gap-4 mt-2 text-xs text-vtal-gray-600 flex-wrap">
                        {activity.inicio && (
                          <span>Início Planejado: {new Date(activity.inicio).toLocaleString('pt-BR', { 
                            day: '2-digit', 
                            month: '2-digit', 
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}</span>
                        )}
                        {activity.fim && (
                          <span>Fim Planejado: {new Date(activity.fim).toLocaleString('pt-BR', { 
                            day: '2-digit', 
                            month: '2-digit', 
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}</span>
                        )}
                        {activity.horario_inicio_real && (
                          <span className="text-green-600 font-semibold">
                            Início Real: {new Date(activity.horario_inicio_real).toLocaleString('pt-BR', { 
                              day: '2-digit', 
                              month: '2-digit', 
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
                        {activity.status || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
                );
              })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-vtal-gray-800">📊 Dashboard Executivo</h1>
        <button
          onClick={loadData}
          className="bg-vtal-secondary hover:bg-vtal-primary text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 font-medium text-sm md:text-base"
        >
          <span>🔄</span>
          <span>Atualizar</span>
        </button>
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

      {/* Indicadores principais */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-vtal-secondary">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Total</p>
              <p className="text-2xl font-display font-bold text-vtal-gray-800 mt-1">{geralSafe.total || 0}</p>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Concluídas</p>
              <p className="text-2xl font-display font-bold text-green-600 mt-1">{geralSafe.concluidas || 0}</p>
            </div>
            <div className="text-2xl">✅</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-blue-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Em Exec. no Prazo</p>
              <p className="text-2xl font-display font-bold text-blue-600 mt-1">{geralSafe.em_execucao_no_prazo || 0}</p>
            </div>
            <div className="text-2xl">⏳</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Em Exec. Fora Prazo</p>
              <p className="text-2xl font-display font-bold text-red-500 mt-1">{geralSafe.em_execucao_fora_prazo || 0}</p>
            </div>
            <div className="text-2xl">🔴</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-blue-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">A Iniciar no Prazo</p>
              <p className="text-2xl font-display font-bold text-blue-800 mt-1">{geralSafe.a_iniciar_no_prazo || 0}</p>
            </div>
            <div className="text-2xl">🟦</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-orange-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">A Iniciar Fora Prazo</p>
              <p className="text-2xl font-display font-bold text-orange-600 mt-1">{geralSafe.a_iniciar_fora_prazo || 0}</p>
            </div>
            <div className="text-2xl">🟠</div>
          </div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Gráfico de Pizza */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-xl font-display font-semibold text-vtal-gray-800 mb-4">
            Distribuição de Status {activeTab !== 'all' ? `- ${SEQUENCIAS_INFO[activeTab]?.nome}` : ''}
          </h3>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-gray-500">
              Nenhum dado disponível para exibir
            </div>
          )}
        </div>

        {/* Gráfico de Barras */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h3 className="text-xl font-display font-semibold text-vtal-gray-800 mb-4">
            Andamento por CRQ {activeTab !== 'all' ? `- ${SEQUENCIAS_INFO[activeTab]?.nome}` : ''}
          </h3>
          {sequenciaData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sequenciaData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="sequencia" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="concluidas" fill="#28a745" name="Concluídas" />
                <Bar dataKey="em_execucao_no_prazo" fill="#3B82F6" name="Em Execução no Prazo" />
                <Bar dataKey="em_execucao_fora_prazo" fill="#EF4444" name="Em Execução Fora do Prazo" />
                <Bar dataKey="a_iniciar_no_prazo" fill="#DBEAFE" name="A Iniciar no Prazo" />
                <Bar dataKey="a_iniciar_fora_prazo" fill="#FED7AA" name="A Iniciar Fora do Prazo" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-300 text-gray-500">
              Nenhum dado disponível para exibir
            </div>
          )}
        </div>
      </div>

      {/* Seções: Em Atraso e Em Andamento */}
      <div className="space-y-4 md:space-y-6">
        <h2 className="text-xl md:text-2xl font-display font-bold text-vtal-gray-800">
          ⚠️ Atividades em Atraso e Em Andamento
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Em Atraso */}
          <ActivityList
            activities={atividadesEmAtraso}
            title="Em Atraso"
            icon="🔴"
            borderColor="border-red-600"
            bgColor="bg-red-50 border-red-200"
          />

          {/* Em Andamento */}
          <ActivityList
            activities={atividadesEmAndamento}
            title="Em Andamento"
            icon="⏳"
            borderColor="border-blue-600"
            bgColor="bg-blue-50 border-blue-200"
          />
        </div>
      </div>

      {/* Listas de Atividades por Status */}
      <div className="space-y-4 md:space-y-6">
        <h2 className="text-xl md:text-2xl font-display font-bold text-vtal-gray-800">
          📋 Lista de Atividades por Status
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Em Execução no Prazo */}
          <ActivityList
            activities={atividadesEmExecucaoNoPrazo}
            title="Em Execução no Prazo"
            icon="⏳"
            borderColor="border-blue-600"
            bgColor="bg-blue-50 border-blue-200"
          />

          {/* Em Execução Fora do Prazo */}
          <ActivityList
            activities={atividadesEmExecucaoForaPrazo}
            title="Em Execução Fora do Prazo"
            icon="🔴"
            borderColor="border-red-500"
            bgColor="bg-red-50 border-red-200"
          />

          {/* A Iniciar no Prazo */}
          <ActivityList
            activities={atividadesAIniciarNoPrazo}
            title="A Iniciar no Prazo"
            icon="🟦"
            borderColor="border-blue-300"
            bgColor="bg-blue-50 border-blue-200"
          />

          {/* A Iniciar Fora do Prazo */}
          <ActivityList
            activities={atividadesAIniciarForaPrazo}
            title="A Iniciar Fora do Prazo"
            icon="🟠"
            borderColor="border-orange-400"
            bgColor="bg-orange-50 border-orange-200"
          />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
