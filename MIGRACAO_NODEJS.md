# 🔄 Guia de Migração para Node.js/React

Este documento descreve a estrutura da versão refatorada em Node.js e React.js.

## 📋 O que foi criado

### Backend (Node.js/Express)

1. **server.js** - Servidor Express principal
2. **database.js** - Gerenciador do banco SQLite (usando better-sqlite3)
3. **config.js** - Configurações da aplicação

### Frontend (React.js)

1. **App.jsx** - Componente principal com roteamento
2. **contexts/AuthContext.jsx** - Contexto de autenticação
3. **components/Layout.jsx** - Layout principal com sidebar
4. **pages/**:
   - **Dashboard.jsx** - Dashboard com gráficos
   - **DataEditor.jsx** - Editor de dados
   - **Communication.jsx** - Geração de mensagem
   - **Settings.jsx** - Configurações e upload
   - **Login.jsx** - Página de login

## 🚀 Como usar

### 1. Instalar dependências do backend

```bash
cd backend
npm install
```

### 2. Instalar dependências do frontend

```bash
cd frontend
npm install
```

### 3. Iniciar backend

```bash
cd backend
npm start
# ou para desenvolvimento com auto-reload:
npm run dev
```

### 4. Iniciar frontend

```bash
cd frontend
npm run dev
```

### 5. Acessar aplicação

- Frontend: http://localhost:5173
- Backend API: http://localhost:3000

## 📦 Dependências Principais

### Backend
- `express` - Framework web
- `better-sqlite3` - Cliente SQLite
- `xlsx` - Processamento de Excel
- `multer` - Upload de arquivos
- `cors` - CORS middleware

### Frontend
- `react` - Biblioteca React
- `react-router-dom` - Roteamento
- `axios` - Cliente HTTP
- `recharts` - Gráficos
- `react-hot-toast` - Notificações

## 🔄 Próximos Passos

1. Implementar autenticação JWT no backend
2. Adicionar mais gráficos no Dashboard
3. Implementar edição inline na tabela
4. Adicionar validações de formulário
5. Implementar testes unitários
6. Adicionar tratamento de erros mais robusto

## 📝 Notas

- O banco de dados SQLite é compartilhado com a versão Python
- A estrutura das tabelas permanece a mesma
- Os dados são compatíveis entre as duas versões
