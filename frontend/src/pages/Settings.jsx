import React, { useState } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';

function Settings() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [showClearModal, setShowClearModal] = useState(false);
  const [confirmText, setConfirmText] = useState('');
  const [clearing, setClearing] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Selecione um arquivo primeiro');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await api.post('/upload-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 300000
      });

      toast.success(`Upload realizado! ${response.data.total_saved} registros salvos.`);
      setFile(null);
      // Resetar input de arquivo
      document.getElementById('file-input').value = '';
    } catch (error) {
      console.error('Erro no upload:', error);
      toast.error(error.response?.data?.error || 'Erro ao fazer upload');
    } finally {
      setUploading(false);
    }
  };

  const handleClearDatabase = async () => {
    if (confirmText !== 'apagar tudo') {
      toast.error('Por favor, digite exatamente "apagar tudo" para confirmar');
      return;
    }

    setClearing(true);
    try {
      const response = await api.delete('/clear-database');
      toast.success(`Base de dados limpa! ${response.data.excel_deleted} registros Excel e ${response.data.control_deleted} controles removidos.`);
      setShowClearModal(false);
      setConfirmText('');
    } catch (error) {
      console.error('Erro ao limpar base de dados:', error);
      toast.error(error.response?.data?.error || 'Erro ao limpar base de dados');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <h1 className="text-2xl md:text-3xl font-display font-bold text-vtal-gray-800">⚙️ Configurações</h1>

      {/* Upload Section */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-display font-semibold text-vtal-gray-800 mb-4">📁 Upload de Arquivo Excel</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-vtal-gray-700 mb-2">
              Selecione o arquivo Excel (.xlsx ou .xls)
            </label>
            <input
              id="file-input"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              className="block w-full text-sm text-vtal-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-vtal-light file:text-vtal-secondary hover:file:bg-vtal-primary hover:file:text-white"
            />
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="bg-vtal-secondary hover:bg-vtal-primary text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <span>{uploading ? '⏳' : '📥'}</span>
            <span>{uploading ? 'Enviando...' : 'Fazer Upload'}</span>
          </button>
        </div>
      </div>

      {/* Limpar Base de Dados */}
      <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-red-500">
        <h2 className="text-xl font-display font-semibold text-vtal-gray-800 mb-4">🗑️ Limpar Base de Dados</h2>
        <div className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold mb-2">⚠️ Atenção: Esta ação é irreversível!</p>
            <p className="text-red-700 text-sm">
              Esta operação irá apagar <strong>TODOS</strong> os dados do banco de dados, incluindo:
            </p>
            <ul className="list-disc list-inside text-red-700 text-sm mt-2 space-y-1">
              <li>Todas as atividades (excel_data)</li>
              <li>Todos os controles de atividades (activity_control)</li>
              <li>Todos os estados de rollback (crq_rollback_state)</li>
            </ul>
          </div>
          <button
            onClick={() => setShowClearModal(true)}
            className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center space-x-2"
          >
            <span>🗑️</span>
            <span>Limpar Base de Dados</span>
          </button>
        </div>
      </div>

      {/* Info Section */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-display font-semibold text-vtal-gray-800 mb-4">📋 Informações da Aplicação</h2>
        <div className="prose max-w-none">
          <p className="text-vtal-gray-700 mb-4">
            <strong>Janela de Mudança TI</strong> é uma aplicação web para gerenciamento de janelas de mudança de TI.
          </p>
          <h3 className="text-lg font-display font-semibold text-vtal-gray-800 mb-2">Funcionalidades:</h3>
          <ul className="list-disc list-inside space-y-2 text-vtal-gray-700">
            <li>✅ Importação de dados de arquivo Excel</li>
            <li>✅ Edição interativa de dados em tempo real</li>
            <li>✅ Dashboard executivo com gráficos e indicadores</li>
            <li>✅ Geração automática de mensagem consolidada</li>
            <li>✅ Persistência de dados em banco SQLite</li>
          </ul>
        </div>
      </div>

      {/* Modal de Confirmação */}
      {showClearModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
            <div className="p-6 border-b border-red-200 bg-red-50">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-display font-semibold text-red-800">⚠️ Confirmar Limpeza</h2>
                <button
                  onClick={() => {
                    setShowClearModal(false);
                    setConfirmText('');
                  }}
                  className="text-red-400 hover:text-red-600 text-2xl"
                  disabled={clearing}
                >
                  ×
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-800 font-semibold mb-2">⚠️ Esta ação é irreversível!</p>
                <p className="text-red-700 text-sm">
                  Todos os dados serão permanentemente removidos do banco de dados.
                </p>
              </div>
              <p className="text-gray-700 mb-4">
                Para confirmar, digite <strong className="text-red-600">"apagar tudo"</strong> no campo abaixo:
              </p>
              <input
                type="text"
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="Digite: apagar tudo"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                disabled={clearing}
                autoFocus
              />
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowClearModal(false);
                  setConfirmText('');
                }}
                disabled={clearing}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancelar
              </button>
              <button
                onClick={handleClearDatabase}
                disabled={confirmText !== 'apagar tudo' || clearing}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {clearing ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    <span>Limpando...</span>
                  </>
                ) : (
                  <>
                    <span>🗑️</span>
                    <span>Limpar Base de Dados</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Settings;
