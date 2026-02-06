/**
 * Configurações da aplicação
 */
const path = require('path');
const fs = require('fs');

// Configurações de diretórios
const BASE_DIR = __dirname;
const DATA_DIR = path.join(BASE_DIR, 'data');
const DB_DIR = path.join(BASE_DIR, 'db');
const DB_PATH = path.join(DB_DIR, 'activity_control.db');

// Configurações de CRQs
const SEQUENCIAS = {
  REDE: { nome: 'REDE', total: 72, emoji: '🟢' },
  OPENSHIFT: { nome: 'OPENSHIFT', total: 39, emoji: '🔵' },
  NFS: { nome: 'NFS', total: 17, emoji: '🟠' },
  SI: { nome: 'SI', total: 25, emoji: '🟡' }
};

const TOTAL_GERAL = 153;

// Status permitidos
const STATUS_OPCOES = [
  'Planejado',
  'Em Execução',
  'Concluído',
  'Atrasado',
  'Adiantado'
];

// Formato de data
const DATE_FORMAT = '%d/%m/%Y %H:%M:%S';
const DATE_FORMAT_DISPLAY = 'DD/MM/AAAA HH:MM:SS';

// Cores para status
const STATUS_COLORS = {
  'Concluído': '#28a745',
  'Em Execução': '#007bff',
  'Planejado': '#ffc107',
  'Atrasado': '#dc3545',
  'Adiantado': '#17a2b8'
};

// Criar diretórios se não existirem
[DATA_DIR, DB_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

module.exports = {
  BASE_DIR,
  DATA_DIR,
  DB_DIR,
  DB_PATH,
  SEQUENCIAS,
  TOTAL_GERAL,
  STATUS_OPCOES,
  DATE_FORMAT,
  DATE_FORMAT_DISPLAY,
  STATUS_COLORS
};
