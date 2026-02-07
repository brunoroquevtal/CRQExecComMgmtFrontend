# 🚀 Como Executar o Projeto Localmente

Este guia explica como executar o frontend localmente, conectado ao backend no Netlify.

## 📋 Pré-requisitos

- Node.js 18+ instalado
- npm ou yarn instalado

## 🔧 Configuração Rápida (Recomendado)

### Usando o Script Automático

Execute o script na raiz do projeto:

```powershell
.\configurar-frontend-local.ps1
```

O script irá:
1. Perguntar qual backend você quer usar
2. Criar automaticamente o arquivo `.env.local` com a configuração correta

### Configuração Manual

#### 1. Instalar Dependências

```bash
cd frontend
npm install
```

#### 2. Configurar Variável de Ambiente

Crie um arquivo `.env.local` na pasta `frontend` com uma das opções abaixo:

**Opção A: Backend no Netlify (Recomendado)**
```env
VITE_API_URL=https://crqcommunidationbackend.netlify.app/api
```

**Opção B: Backend no Netlify usando Functions**
```env
VITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api
```

**Opção C: Backend Local**
```env
VITE_API_URL=http://localhost:3000/api
```

**Opção D: Usar Proxy do Vite (Padrão)**
Não crie o arquivo `.env.local` - o frontend usará o proxy configurado no `vite.config.js`, que redireciona `/api` para `http://localhost:3000`.

### 3. Configurar Supabase (Opcional)

Se você quiser usar autenticação com Supabase, adicione estas variáveis ao `.env.local`:

```env
VITE_SUPABASE_URL=https://seu-projeto.supabase.co
VITE_SUPABASE_ANON_KEY=sua-chave-anon
```

**Nota:** Se você não configurar o Supabase, o sistema funcionará normalmente, mas a autenticação não estará disponível. Você verá um aviso no console, mas isso não impede o uso da aplicação.

## 🚀 Executar o Projeto

Após configurar a variável de ambiente, execute:

```bash
cd frontend
npm run dev
```

O frontend estará disponível em: **http://localhost:5173**

## 🔍 Verificar Configuração

Para verificar qual URL está sendo usada:

1. Abra o DevTools do navegador (F12)
2. Vá na aba **Console**
3. Você verá logs indicando a URL base da API
4. Ou vá na aba **Network** e veja para onde as requisições estão sendo enviadas

## 📝 Arquivos de Configuração

- **`.env.local`** - Variáveis de ambiente locais (não commitado no git)
- **`.env.example`** - Exemplo de configuração (commitado no git)
- **`vite.config.js`** - Configuração do Vite com proxy para desenvolvimento

## 🐛 Solução de Problemas

### Erro de CORS

Se você receber erros de CORS ao acessar o backend no Netlify:

1. Verifique se o backend está configurado para aceitar requisições do localhost
2. Verifique se a URL do backend está correta
3. Tente usar o backend local se o problema persistir

### Requisições não funcionam

1. Verifique se a variável `VITE_API_URL` está definida corretamente
2. Certifique-se de que o arquivo `.env.local` está na pasta `frontend`
3. Reinicie o servidor de desenvolvimento após alterar `.env.local`
4. Verifique os logs do console do navegador para erros

### Backend não responde

1. Teste a URL do backend diretamente no navegador:
   - `https://crqcommunidationbackend.netlify.app/health`
2. Verifique se o backend está online no Netlify Dashboard
3. Verifique os logs do backend no Netlify

## 📚 Mais Informações

- [Documentação do Vite](https://vitejs.dev/)
- [Variáveis de Ambiente no Vite](https://vitejs.dev/guide/env-and-mode.html)
