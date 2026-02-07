# 🔧 Solução para HTTP 500 no Netlify

## 🔴 Problema

A API no Netlify está retornando **HTTP 500** com erro "Invalid API key" ao tentar fazer requisições PUT para `/api/activity`.

## 🔍 Possíveis Causas

### 1. Problema com Netlify Functions

O backend está configurado como Netlify Functions usando `serverless-http`. O erro 500 pode indicar:

- **Erro no wrapper serverless-http**: O wrapper pode não estar funcionando corretamente
- **Problema com o caminho do módulo**: O `require` pode estar falhando
- **Timeout**: Netlify Functions tem limite de tempo (10s para free tier, 26s para pro)

### 2. Erro no Código do Backend

- **Erro não tratado**: Algum erro JavaScript não está sendo capturado
- **Problema com banco de dados**: Conexão com Supabase/SQLite pode estar falhando
- **Variáveis de ambiente**: Variáveis necessárias podem não estar configuradas no Netlify

### 3. Problema com a Rota Específica

- **PUT /api/activity**: Esta rota pode ter algum problema específico
- **Validação de dados**: O backend pode estar rejeitando os dados enviados

## ✅ Soluções

### Solução 1: Verificar Logs do Netlify

1. Acesse o **Netlify Dashboard**
2. Vá em **Functions** > **Logs**
3. Procure por erros recentes
4. Verifique a mensagem de erro completa

### Solução 2: Verificar Variáveis de Ambiente no Netlify

No Netlify Dashboard:
1. Vá em **Site settings** > **Environment variables**
2. Verifique se todas as variáveis necessárias estão configuradas:
   - `SUPABASE_URL` (se usando Supabase)
   - `SUPABASE_ANON_KEY` (se usando Supabase)
   - `API_DEBUG` (opcional)
   - `PORT` (não necessário para Functions)

### Solução 3: Testar Health Check

O health check funciona? Teste:

```powershell
Invoke-RestMethod -Uri "https://crqcommunidationbackend.netlify.app/health"
```

Se funcionar, o problema é específico da rota `/api/activity`.

### Solução 4: Verificar Código do Backend

Verifique se o arquivo `backend/netlify/functions/api.js` existe e está correto:

```javascript
const serverless = require('serverless-http');
const app = require('../../server.js');

module.exports.handler = serverless(app);
```

### Solução 5: Adicionar Tratamento de Erros

O backend pode estar lançando erros não tratados. Verifique se todas as rotas têm `try/catch`.

### Solução 6: Verificar Timeout

Netlify Functions tem limite de tempo. Se a requisição demorar muito, pode dar timeout.

**Solução**: Otimizar o código ou usar Netlify Pro para timeouts maiores.

### Solução 7: Testar Localmente com Serverless

Teste o backend localmente usando o serverless:

```bash
cd backend
npm install -g netlify-cli
netlify dev
```

Isso simula o ambiente do Netlify localmente.

## 🧪 Teste Manual

Teste a rota diretamente:

```powershell
$body = @{
    seq = 1
    sequencia = "REDE"
    atividade = "Teste de atividade"
    inicio = "01/01/2024 10:00:00"
    fim = "01/01/2024 11:00:00"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod `
        -Uri "https://crqcommunidationbackend.netlify.app/api/activity" `
        -Method Put `
        -Body $body `
        -ContentType "application/json"
    Write-Host "Sucesso:" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "Erro:" -ForegroundColor Red
    $_.Exception.Response.StatusCode
    $_.Exception.Message
}
```

## 📋 Checklist de Diagnóstico

- [ ] Verificar logs do Netlify Functions
- [ ] Verificar variáveis de ambiente no Netlify
- [ ] Testar health check (`/health`)
- [ ] Verificar se `netlify/functions/api.js` existe
- [ ] Verificar se `serverless-http` está instalado
- [ ] Testar localmente com `netlify dev`
- [ ] Verificar se há erros no código do backend
- [ ] Verificar timeout das requisições

## 🔗 Próximos Passos

1. **Verifique os logs do Netlify** - Isso dará a causa exata do erro
2. **Teste localmente** - Use `netlify dev` para simular o ambiente
3. **Simplifique a requisição** - Teste com dados mínimos primeiro
4. **Verifique o banco de dados** - Se usando Supabase, verifique conexão

## 📝 Nota Importante

O erro "Invalid API key" pode ser uma mensagem genérica. O verdadeiro erro pode estar nos logs do Netlify. Sempre verifique os logs primeiro!
