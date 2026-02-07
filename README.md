# 🎨 CRQ Exec Com Mgmt - Frontend

Frontend React para gerenciamento de janelas de mudança de TI.

## 📋 Instalação

```bash
npm install
npm run dev
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto frontend:

**Para desenvolvimento local:**
```env
VITE_API_URL=http://localhost:3000/api
```

**Para produção (com backend no Netlify):**
```env
VITE_API_URL=https://seu-backend.netlify.app/api
```

**Nota:** Se não definir `VITE_API_URL`, o frontend usará `/api` como padrão (proxy do Vite em desenvolvimento).

### Proxy de Desenvolvimento

O Vite está configurado para fazer proxy das requisições `/api` para `http://localhost:3000` durante o desenvolvimento.

## 🚀 Scripts Disponíveis

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Gera build de produção
- `npm run preview` - Preview do build de produção

## 🎨 Funcionalidades

- **Dashboard**: Gráficos e indicadores em tempo real
- **Editor de Dados**: Edição de atividades
- **Comunicação**: Geração de mensagem de comunicação
- **Configurações**: Upload de Excel e limpeza de dados
- **Planejamento**: Visualização em Gantt

## 📦 Dependências Principais

- `react` - Biblioteca React
- `react-router-dom` - Roteamento
- `axios` - Cliente HTTP
- `recharts` - Gráficos
- `react-hot-toast` - Notificações
- `tailwindcss` - Framework CSS
- `vite` - Build tool

## 🔗 Backend

O backend está disponível em: [CRQExecComMgmtBackend](https://github.com/SEU_USUARIO/CRQExecComMgmtBackend)

## 📝 Notas

- O frontend se conecta ao backend através da API REST
- Certifique-se de que o backend está rodando antes de iniciar o frontend
- Para produção, configure a variável `VITE_API_URL` com a URL do backend em produção