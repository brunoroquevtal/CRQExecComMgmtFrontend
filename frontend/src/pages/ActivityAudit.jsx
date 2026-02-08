import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import api from '../utils/api';
import toast from 'react-hot-toast';

function ActivityAudit() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [migrating, setMigrating] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [filters, setFilters] = useState({
    was_accepted: '',
    was_saved: '',
    sequencia: '',
    seq: ''
  });

  useEffect(() => {
    loadRecords();
  }, [filters]);

  const loadRecords = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.was_accepted !== '') {
        params.append('was_accepted', filters.was_accepted);
      }
      if (filters.was_saved !== '') {
        params.append('was_saved', filters.was_saved);
      }
      if (filters.sequencia) {
        params.append('sequencia', filters.sequencia);
      }
      if (filters.seq) {
        params.append('seq', filters.seq);
      }

      const response = await api.get(`/activity-audit?${params.toString()}`);
      setRecords(response.data.records || []);
    } catch (error) {
      console.error('Erro ao carregar registros de auditoria:', error);
      toast.error('Erro ao carregar registros de auditoria');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      const allIds = new Set(records.map(r => r.id));
      setSelectedIds(allIds);
    } else {
      setSelectedIds(new Set());
    }
  };

  const handleSelectRecord = (id, checked) => {
    const newSelected = new Set(selectedIds);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedIds(newSelected);
  };

  const handleMigrate = async () => {
    if (selectedIds.size === 0) {
      toast.error('Selecione pelo menos um registro para migrar');
      return;
    }

    if (!confirm(`Deseja migrar ${selectedIds.size} registro(s) para a tabela activities?`)) {
      return;
    }

    setMigrating(true);
    try {
      const response = await api.post('/activity-audit/migrate', {
        audit_ids: Array.from(selectedIds)
      });

      const result = response.data.result;
      toast.success(
        `Migração concluída: ${result.migrated.length} migrados, ${result.errors.length} erros, ${result.skipped.length} ignorados`
      );

      // Limpar seleção e recarregar
      setSelectedIds(new Set());
      loadRecords();
    } catch (error) {
      console.error('Erro ao migrar registros:', error);
      toast.error(error.response?.data?.error || 'Erro ao migrar registros');
    } finally {
      setMigrating(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), "dd/MM/yyyy HH:mm:ss", { locale: ptBR });
    } catch {
      return dateString;
    }
  };

  const getStatusBadge = (wasAccepted, wasSaved) => {
    if (wasSaved === 1 || wasSaved === true) {
      return <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">Salvo</span>;
    }
    if (wasAccepted === 1 || wasAccepted === true) {
      return <span className="px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-800">Aceito</span>;
    }
    return <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-800">Rejeitado</span>;
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Auditoria de Atividades</h1>
        <p className="text-gray-600">
          Consulte registros da tabela activity_audit e migre para a tabela activities
        </p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aceito
            </label>
            <select
              value={filters.was_accepted}
              onChange={(e) => setFilters({ ...filters, was_accepted: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vtal-primary"
            >
              <option value="">Todos</option>
              <option value="true">Sim</option>
              <option value="false">Não</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Salvo
            </label>
            <select
              value={filters.was_saved}
              onChange={(e) => setFilters({ ...filters, was_saved: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vtal-primary"
            >
              <option value="">Todos</option>
              <option value="true">Sim</option>
              <option value="false">Não</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              CRQ (Sequência)
            </label>
            <input
              type="text"
              value={filters.sequencia}
              onChange={(e) => setFilters({ ...filters, sequencia: e.target.value })}
              placeholder="Ex: CRQ123456"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vtal-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Seq
            </label>
            <input
              type="number"
              value={filters.seq}
              onChange={(e) => setFilters({ ...filters, seq: e.target.value })}
              placeholder="Ex: 1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-vtal-primary"
            />
          </div>
        </div>
      </div>

      {/* Ações */}
      <div className="bg-white rounded-lg shadow p-4 mb-6 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {selectedIds.size} de {records.length} selecionado(s)
          </span>
          <button
            onClick={() => handleSelectAll(selectedIds.size !== records.length)}
            className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition"
          >
            {selectedIds.size === records.length ? 'Desmarcar Todos' : 'Selecionar Todos'}
          </button>
        </div>
        <button
          onClick={handleMigrate}
          disabled={selectedIds.size === 0 || migrating}
          className="px-6 py-2 bg-vtal-primary text-white rounded-md hover:bg-vtal-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {migrating ? 'Migrando...' : `Migrar ${selectedIds.size} Registro(s)`}
        </button>
      </div>

      {/* Tabela */}
      <div className="bg-white rounded-lg shadow overflow-x-auto">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-primary mx-auto"></div>
            <p className="mt-4 text-gray-600">Carregando registros...</p>
          </div>
        ) : records.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            Nenhum registro encontrado
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={selectedIds.size === records.length && records.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Seq / CRQ
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Atividade
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Aceito / Salvo
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recebido em
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Motivos de Rejeição
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {records.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedIds.has(record.id)}
                      onChange={(e) => handleSelectRecord(record.id, e.target.checked)}
                      className="rounded border-gray-300"
                    />
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {record.id}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    <div>
                      <div className="font-medium">Seq: {record.seq || 'N/A'}</div>
                      <div className="text-gray-500">CRQ: {record.sequencia || 'N/A'}</div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    <div className="max-w-xs truncate" title={record.atividade || 'N/A'}>
                      {record.atividade || 'N/A'}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {record.status || 'N/A'}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {getStatusBadge(record.was_accepted, record.was_saved)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {formatDate(record.received_at)}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {record.rejection_reasons && record.rejection_reasons.length > 0 ? (
                      <div className="max-w-xs">
                        {record.rejection_reasons.map((reason, idx) => (
                          <div key={idx} className="text-red-600 text-xs">
                            • {reason}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default ActivityAudit;
