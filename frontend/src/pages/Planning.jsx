import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import GanttChart from '../components/GanttChart';

const SEQUENCIAS = ['REDE', 'OPENSHIFT', 'NFS', 'SI'];

const SEQUENCIAS_INFO = {
  REDE: { nome: 'REDE', color: 'text-green-600' },
  OPENSHIFT: { nome: 'OPENSHIFT', color: 'text-blue-600' },
  NFS: { nome: 'NFS', color: 'text-orange-600' },
  SI: { nome: 'SI', color: 'text-yellow-600' }
};

function Planning() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      const response = await axios.get('/api/activities');
      setActivities(response.data.activities || []);
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar atividades:', error);
      toast.error('Erro ao carregar atividades');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary mx-auto"></div>
          <p className="mt-4 text-vtal-gray-600">Carregando atividades...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-vtal-gray-800">
          📅 Planejamento
        </h1>
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
              return (
                <button
                  key={seq}
                  onClick={() => setActiveTab(seq)}
                  className={`py-3 md:py-4 px-1 border-b-2 font-medium text-xs md:text-sm transition-colors whitespace-nowrap ${
                    activeTab === seq
                      ? 'border-vtal-secondary text-vtal-secondary'
                      : 'border-transparent text-vtal-gray-600 hover:text-vtal-gray-800 hover:border-vtal-gray-300'
                  }`}
                >
                  <span className={activeTab === seq ? SEQUENCIAS_INFO[seq].color : ''}>
                    <span className="hidden sm:inline">{SEQUENCIAS_INFO[seq].nome}</span>
                    <span className="sm:hidden">{SEQUENCIAS_INFO[seq].nome.substring(0, 3)}</span>
                  </span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Gráfico de Gantt */}
      <GanttChart activities={activities} activeTab={activeTab} />
    </div>
  );
}

export default Planning;
