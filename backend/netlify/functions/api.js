/**
 * Netlify Function wrapper para o servidor Express
 * Permite que o backend Express funcione como Netlify Function
 */
const serverless = require('serverless-http');
const app = require('../../server.js');

// Exportar handler para Netlify Functions
module.exports.handler = serverless(app);
