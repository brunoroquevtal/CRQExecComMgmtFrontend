# 🔍 Arquitetura de Chamadas - Frontend

Este documento descreve como o frontend faz chamadas ao Supabase e à API do backend.

## 📊 Resumo Geral

O sistema usa um **modelo híbrido**:
- **Autenticação**: Chamadas diretas ao Supabase
- **Dados da aplicação**: Chamadas via API do backend
- **Token de autenticação**: Obtido do Supabase e enviado nas requisições da API

## 🔐 Autenticação (Supabase Direto)

### Login
```javascript
// AuthContext.jsx:96
supabase.auth.signInWithPassword({ email, password })
```
- ✅ **Direto ao Supabase** - Não passa pelo backend

### Logout
```javascript
// AuthContext.jsx:173
supabase.auth.signOut()
```
- ✅ **Direto ao Supabase** - Não passa pelo backend

### Signup (Cadastro)
```javascript
// AuthContext.jsx:133
supabase.auth.signUp({ email, password })
```
- ✅ **Direto ao Supabase** - Não passa pelo backend
- ⚠️ Mas valida domínio via API antes: `api.post('/auth/signup')`

### Verificação de Sessão
```javascript
// AuthContext.jsx:31, 43, 62, 196
supabase.auth.getSession()
supabase.auth.onAuthStateChange()
```
- ✅ **Direto ao Supabase** - Para verificar se usuário está autenticado

## 📡 Dados da Aplicação (API do Backend)

Todas as operações de negócio passam pela API do backend:

### Dashboard
```javascript
// Dashboard.jsx:51
api.get('/statistics')
```
- ✅ **Via API do backend** - Estatísticas e métricas

### Editor de Dados
```javascript
// DataEditor.jsx:165, 303, 333
api.get('/activities')        // Listar atividades
api.put('/activity')          // Atualizar atividade
api.delete('/activity')       // Deletar atividade
```
- ✅ **Via API do backend** - CRUD de atividades

### Planejamento
```javascript
// Planning.jsx:26
api.get('/activities')
```
- ✅ **Via API do backend** - Listar atividades para Gantt

### Comunicação
```javascript
// Communication.jsx:18
api.get('/message')           // Mensagem padrão
api.get('/message-detailed')  // Mensagem detalhada
```
- ✅ **Via API do backend** - Gerar mensagens

### Configurações
```javascript
// Settings.jsx:27, 54
api.post('/upload-excel')     // Upload de arquivo
api.delete('/clear-database') // Limpar banco
```
- ✅ **Via API do backend** - Upload e manutenção

### Perfil do Usuário
```javascript
// AuthContext.jsx:69
api.get('/auth/profile')
```
- ✅ **Via API do backend** - Dados do perfil (role, nome, etc.)

### Validações
```javascript
// AuthContext.jsx:126
api.post('/auth/signup')      // Validar domínio antes de cadastrar

// Signup.jsx:22
api.get('/auth/allowed-domains') // Listar domínios permitidos
```
- ✅ **Via API do backend** - Validações e regras de negócio

## 🔑 Token de Autenticação

O token do Supabase é automaticamente adicionado nas requisições da API:

```javascript
// api.js:26-35
api.interceptors.request.use(async (config) => {
  if (supabase) {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`;
    }
  }
  return config;
});
```

**Fluxo:**
1. Usuário faz login no Supabase → recebe token
2. Frontend armazena token na sessão do Supabase
3. Todas as requisições `api.get/post/put/delete` → token é adicionado automaticamente
4. Backend valida token com Supabase → autoriza requisição

## 📋 Fluxo Completo de Autenticação

```
1. Login:
   Frontend → Supabase (signInWithPassword)
   ↓
   Supabase retorna token
   ↓
   Frontend armazena token
   ↓
   Frontend → API Backend (/auth/profile) com token
   ↓
   Backend valida token com Supabase
   ↓
   Backend retorna perfil do usuário
```

## 🎯 Resumo por Tipo de Operação

| Operação | Destino | Método |
|----------|---------|--------|
| Login | Supabase | Direto |
| Logout | Supabase | Direto |
| Signup | Supabase | Direto |
| Verificar sessão | Supabase | Direto |
| Obter perfil | API Backend | `api.get('/auth/profile')` |
| Validar domínio | API Backend | `api.post('/auth/signup')` |
| Listar domínios | API Backend | `api.get('/auth/allowed-domains')` |
| Estatísticas | API Backend | `api.get('/statistics')` |
| Atividades | API Backend | `api.get('/activities')` |
| Atualizar atividade | API Backend | `api.put('/activity')` |
| Deletar atividade | API Backend | `api.delete('/activity')` |
| Upload Excel | API Backend | `api.post('/upload-excel')` |
| Limpar banco | API Backend | `api.delete('/clear-database')` |
| Gerar mensagem | API Backend | `api.get('/message')` |

## ⚠️ Importante

1. **Autenticação é feita diretamente no Supabase** - O backend não gerencia login/logout
2. **Dados da aplicação vão para o backend** - Todas as operações de negócio passam pela API
3. **Token é compartilhado** - Token do Supabase é usado para autenticar requisições na API
4. **Backend valida token** - O backend verifica o token do Supabase antes de processar requisições

## 🔧 Configuração Necessária

### Frontend
- `VITE_API_URL` - URL do backend (ex: `https://crqcommunidationbackend.netlify.app/api`)
- `VITE_SUPABASE_URL` - URL do projeto Supabase (opcional)
- `VITE_SUPABASE_ANON_KEY` - Chave anônima do Supabase (opcional)

### Backend
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_SERVICE_ROLE_KEY` - Chave de serviço do Supabase (para validar tokens)
- `SUPABASE_ANON_KEY` - Chave anônima (para operações públicas)
