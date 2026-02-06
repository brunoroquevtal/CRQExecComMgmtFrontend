# 🚀 Janela de Mudança TI - Versão Node.js/React

Esta é a versão refatorada da aplicação em Node.js (Express) e React.js.

## 📁 Estrutura do Projeto

```
CRQMinAMin/
├── backend/                 # API Node.js/Express
│   ├── server.js           # Servidor principal
│   ├── database.js         # Gerenciamento SQLite
│   ├── config.js           # Configurações
│   ├── package.json
│   └── .env.example
├── frontend/                # Aplicação React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── contexts/       # Context API (Auth)
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── db/                      # Banco de dados SQLite (compartilhado)
```

## 🚀 Instalação

### Backend

```bash
cd backend
npm install
cp .env.example .env
npm start
# ou para desenvolvimento:
npm run dev
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuração

### Backend (.env)

```env
PORT=3000
API_DEBUG=false
API_BASE_URL=http://localhost:3000
```

### Frontend

O frontend está configurado para fazer proxy das requisições `/api` para `http://localhost:3000`.

## 📡 Endpoints da API

- `GET /health` - Health check
- `GET /` - Informações da API
- `POST /api/upload-excel` - Upload de arquivo Excel
- `GET /api/activities` - Listar todas as atividades
- `GET /api/activity/:sequencia/:seq` - Obter atividade específica
- `PUT /api/activity` - Atualizar atividade
- `GET /api/statistics` - Obter estatísticas
- `GET /api/message` - Gerar mensagem de comunicação

## 🎨 Funcionalidades do Frontend

- **Dashboard**: Gráficos e indicadores
- **Editor de Dados**: Edição de atividades
- **Comunicação**: Geração de mensagem
- **Configurações**: Upload de Excel

## 🔐 Autenticação

Usuários de teste:
- `admin` / `admin123`
- `lider` / `lider123`
- `visualizador` / `view123`

## 📝 Notas

- O banco de dados SQLite é compartilhado entre Python e Node.js
- A estrutura do banco permanece a mesma
- Os dados são compatíveis entre as duas versões
