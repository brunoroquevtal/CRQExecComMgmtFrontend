# 🔍 Verificar Por Que o Frontend Não Mostra Dados

## 🔴 Problema

Você vê dados no Supabase, mas o frontend não mostra nada.

## 🔍 Possíveis Causas

### 1. URL da API Não Configurada no Netlify

O frontend usa a variável de ambiente `VITE_API_URL`. Se não estiver configurada, ele tenta usar `/api` (relativo), que não funciona no Netlify.

**Solução**: Configure a variável de ambiente no Netlify:

1. Acesse o **Netlify Dashboard**
2. Selecione o site do **frontend**
3. Vá em **Site settings** > **Environment variables**
4. Adicione:
   ```
   VITE_API_URL = https://crqcommunidationbackend.netlify.app/api
   ```
5. Faça um novo deploy

### 2. CORS Não Configurado

O backend pode estar bloqueando requisições do frontend.

**Verificar**: Abra o console do navegador (F12) e veja se há erros de CORS.

### 3. Erro na Resposta da API

A API pode estar retornando dados em formato diferente do esperado.

**Verificar**: 
- Abra o console do navegador (F12)
- Vá em **Network**
- Procure por requisições para `/api/statistics` ou `/api/activities`
- Veja a resposta da API

### 4. Estrutura de Dados Diferente

O Supabase pode estar retornando dados em formato diferente do esperado pelo frontend.

## ✅ Passos para Diagnosticar

### Passo 1: Verificar Console do Navegador

1. Abra o frontend no navegador
2. Pressione **F12** para abrir DevTools
3. Vá na aba **Console**
4. Procure por erros (vermelho)
5. Vá na aba **Network**
6. Recarregue a página
7. Procure por requisições para `/api/statistics` ou `/api/activities`
8. Clique na requisição e veja:
   - **Status**: Deve ser 200 (OK)
   - **Response**: Veja o que a API está retornando

### Passo 2: Verificar Variável de Ambiente

No console do navegador, execute:

```javascript
console.log('API URL:', import.meta.env.VITE_API_URL);
```

Se mostrar `undefined`, a variável não está configurada.

### Passo 3: Testar API Diretamente

Teste a API diretamente no navegador:

```
https://crqcommunidationbackend.netlify.app/api/statistics
```

Ou:

```
https://crqcommunidationbackend.netlify.app/api/activities
```

### Passo 4: Verificar Estrutura dos Dados

A API deve retornar:

**Para `/api/statistics`:**
```json
{
  "geral": {
    "total": 10,
    "concluidas": 5,
    "em_execucao_no_prazo": 2,
    ...
  },
  "por_sequencia": {
    "REDE": { ... },
    ...
  }
}
```

**Para `/api/activities`:**
```json
{
  "activities": [
    { "seq": 1, "sequencia": "REDE", ... },
    ...
  ]
}
```

## 🔧 Solução Rápida

### Configurar VITE_API_URL no Netlify

1. **Netlify Dashboard** > Seu site do frontend
2. **Site settings** > **Environment variables**
3. Adicione:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://crqcommunidationbackend.netlify.app/api`
4. **Save**
5. **Deploy** > **Trigger deploy** > **Clear cache and deploy site**

### Verificar CORS no Backend

O backend deve ter CORS configurado para aceitar requisições do frontend. Verifique se o `server.js` tem:

```javascript
app.use(cors());
```

## 🧪 Teste Manual

Abra o console do navegador e execute:

```javascript
// Testar se a API está acessível
fetch('https://crqcommunidationbackend.netlify.app/api/statistics')
  .then(r => r.json())
  .then(data => console.log('Dados:', data))
  .catch(err => console.error('Erro:', err));
```

## 📋 Checklist

- [ ] Variável `VITE_API_URL` configurada no Netlify
- [ ] Deploy do frontend realizado após configurar variável
- [ ] Console do navegador verificado (sem erros)
- [ ] Network tab verificado (requisições sendo feitas)
- [ ] API testada diretamente (retorna dados)
- [ ] CORS configurado no backend
- [ ] Estrutura de dados correta
