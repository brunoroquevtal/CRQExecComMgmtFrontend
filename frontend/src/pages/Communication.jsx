import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

function Communication() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [messageType, setMessageType] = useState('standard'); // 'standard' ou 'detailed'

  useEffect(() => {
    loadMessage();
  }, [messageType]);

  const loadMessage = async () => {
    setLoading(true);
    try {
      const endpoint = messageType === 'detailed' ? '/api/message-detailed' : '/api/message';
      const response = await axios.get(endpoint);
      setMessage(response.data.message || '');
      setLoading(false);
    } catch (error) {
      console.error('Erro ao carregar mensagem:', error);
      toast.error('Erro ao gerar mensagem');
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message);
    toast.success('Mensagem copiada para a área de transferência!');
  };

  return (
    <div className="space-y-4 md:space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl md:text-3xl font-display font-bold text-vtal-gray-800">💬 Comunicação</h1>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-4 w-full sm:w-auto">
          <div className="flex items-center space-x-2 bg-white rounded-lg p-1 border border-vtal-gray-300">
            <button
              onClick={() => setMessageType('standard')}
              className={`px-3 md:px-4 py-2 rounded-md transition-colors font-medium text-sm md:text-base ${
                messageType === 'standard'
                  ? 'bg-vtal-secondary text-white'
                  : 'text-vtal-gray-700 hover:bg-vtal-gray-100'
              }`}
            >
              📊 Padrão
            </button>
            <button
              onClick={() => setMessageType('detailed')}
              className={`px-3 md:px-4 py-2 rounded-md transition-colors font-medium text-sm md:text-base ${
                messageType === 'detailed'
                  ? 'bg-vtal-secondary text-white'
                  : 'text-vtal-gray-700 hover:bg-vtal-gray-100'
              }`}
            >
              📋 Detalhada
            </button>
          </div>
          <button
            onClick={loadMessage}
            disabled={loading}
            className="bg-vtal-secondary hover:bg-vtal-primary text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 font-medium text-sm md:text-base"
          >
            <span>🔄</span>
            <span className="hidden sm:inline">{loading ? 'Carregando...' : 'Atualizar Mensagem'}</span>
            <span className="sm:hidden">{loading ? '...' : 'Atualizar'}</span>
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="mb-4 flex justify-end">
          <button
            onClick={copyToClipboard}
            className="bg-vtal-success hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2 font-medium"
          >
            <span>📋</span>
            <span>Copiar Mensagem</span>
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-vtal-secondary"></div>
          </div>
        ) : (
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={20}
            className="w-full px-4 py-3 border border-vtal-gray-300 rounded-lg focus:ring-2 focus:ring-vtal-secondary focus:border-transparent font-mono text-sm"
            placeholder="A mensagem será gerada automaticamente..."
          />
        )}
      </div>
    </div>
  );
}

export default Communication;
