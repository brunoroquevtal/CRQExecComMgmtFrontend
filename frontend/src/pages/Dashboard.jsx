import React, { useState, useEffect } from 'react';
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
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const statsRes = await api.get('/statistics');
      setStatistics(statsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast.error('Erro ao carregar dados do dashboard');
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

  // Dados para gráfico de pizza (status)
  const statusData = [
    { name: 'Concluídas', value: geral.concluidas || 0, color: '#28a745' },
    { name: 'Em Execução no Prazo', value: geral.em_execucao_no_prazo || 0, color: '#3B82F6' },
    { name: 'Em Execução Fora do Prazo', value: geral.em_execucao_fora_prazo || 0, color: '#EF4444' },
    { name: 'A Iniciar no Prazo', value: geral.a_iniciar_no_prazo || 0, color: '#DBEAFE' },
    { name: 'A Iniciar Fora do Prazo', value: geral.a_iniciar_fora_prazo || 0, color: '#FED7AA' }
  ].filter(item => item.value > 0);

  // Dados para gráfico de barras (por sequência)
  const sequenciaData = Object.entries(por_sequencia).map(([seq, stats]) => ({
    sequencia: seq,
    concluidas: stats.concluidas || 0,
    em_execucao_no_prazo: stats.em_execucao_no_prazo || 0,
    em_execucao_fora_prazo: stats.em_execucao_fora_prazo || 0,
    a_iniciar_no_prazo: stats.a_iniciar_no_prazo || 0,
    a_iniciar_fora_prazo: stats.a_iniciar_fora_prazo || 0
  }));

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
              <p className="text-2xl font-display font-bold text-vtal-gray-800 mt-1">{geral.total || 0}</p>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Concluídas</p>
              <p className="text-2xl font-display font-bold text-green-600 mt-1">{geral.concluidas || 0}</p>
            </div>
            <div className="text-2xl">✅</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-blue-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Em Exec. no Prazo</p>
              <p className="text-2xl font-display font-bold text-blue-600 mt-1">{geral.em_execucao_no_prazo || 0}</p>
            </div>
            <div className="text-2xl">⏳</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">Em Exec. Fora Prazo</p>
              <p className="text-2xl font-display font-bold text-red-500 mt-1">{geral.em_execucao_fora_prazo || 0}</p>
            </div>
            <div className="text-2xl">🔴</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-blue-300">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">A Iniciar no Prazo</p>
              <p className="text-2xl font-display font-bold text-blue-800 mt-1">{geral.a_iniciar_no_prazo || 0}</p>
            </div>
            <div className="text-2xl">🟦</div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-3 border-l-4 border-orange-400">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-vtal-gray-600 text-xs font-medium">A Iniciar Fora Prazo</p>
              <p className="text-2xl font-display font-bold text-orange-600 mt-1">{geral.a_iniciar_fora_prazo || 0}</p>
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
    </div>
  );
}

export default Dashboard;
