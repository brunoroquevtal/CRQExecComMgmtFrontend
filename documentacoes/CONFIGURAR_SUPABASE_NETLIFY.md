# 🔧 Configurar Supabase no Netlify

## 🔴 Problema Identificado

Os logs do Netlify mostram erros do Supabase:
- `Erro ao conectar ao Supabase: ECONNRESET`
- `Invalid API key` - "Double check your Supabase `anon` or `service_role` API key"

Isso indica que o backend está tentando usar Supabase, mas as variáveis de ambiente não estão configuradas no Netlify.

## ✅ Solução: Configurar Variáveis de Ambiente no Netlify

### Passo 1: Obter Credenciais do Supabase

1. Acesse seu projeto no [Supabase Dashboard](https://app.supabase.com)
2. Vá em **Settings** > **API**
3. Copie:
   - **Project URL** (ex: `https://xxxxx.supabase.co`)
   - **anon public key** (chave pública)
   - **service_role key** (chave privada - use com cuidado!)

### Passo 2: Configurar no Netlify

1. Acesse o **Netlify Dashboard**
2. Selecione seu site do backend
3. Vá em **Site settings** > **Environment variables**
4. Adicione as seguintes variáveis:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_ANON_KEY=sua-chave-anon-key
```

**Importante**: 
- Use `SUPABASE_ANON_KEY` para operações normais
- `SUPABASE_SERVICE_ROLE_KEY` só se precisar de permissões elevadas (geralmente não necessário)

### Passo 3: Verificar se o Backend Usa Supabase

Se o backend está configurado para usar Supabase quando as variáveis estão presentes, você tem duas opções:

#### Opção A: Usar Supabase (Recomendado para Produção)

1. Configure as variáveis acima
2. Faça um novo deploy
3. Verifique os logs

#### Opção B: Usar SQLite (Mais Simples)

Se você não quer usar Supabase no Netlify:

1. **NÃO configure** as variáveis `SUPABASE_URL` e `SUPABASE_ANON_KEY`
2. O backend deve usar SQLite por padrão
3. **Problema**: SQLite não funciona bem em ambientes serverless (Netlify Functions)
4. **Solução**: Use Supabase ou migre para outra plataforma (Railway, Render)

## 🔍 Verificar Código do Backend

O backend pode estar detectando automaticamente se deve usar Supabase:

```javascript
// Exemplo de lógica (verificar no código real)
if (process.env.SUPABASE_URL && process.env.SUPABASE_ANON_KEY) {
  // Usar Supabase
  const DatabaseManager = require('./database-supabase');
} else {
  // Usar SQLite
  const DatabaseManager = require('./database');
}
```

## 📋 Checklist

- [ ] Credenciais do Supabase obtidas
- [ ] Variáveis de ambiente configuradas no Netlify:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_ANON_KEY`
- [ ] Novo deploy realizado
- [ ] Logs verificados após deploy
- [ ] Teste da API realizado

## 🧪 Testar Após Configuração

Execute o script de teste:

```powershell
.\testar_api_netlify.ps1
```

Ou teste manualmente:

```powershell
Invoke-RestMethod -Uri "https://crqcommunidationbackend.netlify.app/health"
```

## ⚠️ Nota Importante

**SQLite não funciona em Netlify Functions** porque:
- O sistema de arquivos é read-only (exceto `/tmp`)
- SQLite precisa escrever arquivos de banco de dados
- Mesmo em `/tmp`, os dados são perdidos entre invocações

**Solução**: Use Supabase (PostgreSQL) ou migre para Railway/Render que suportam SQLite melhor.

## 🔗 Próximos Passos

1. Configure as variáveis do Supabase no Netlify
2. Faça um novo deploy
3. Verifique os logs
4. Teste a API

Se ainda houver problemas, verifique:
- Se as chaves do Supabase estão corretas
- Se o projeto Supabase está ativo
- Se há problemas de rede/firewall
