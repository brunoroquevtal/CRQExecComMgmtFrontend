# 🔧 Configurar Submodule Privado no Netlify

O Netlify precisa de permissão para clonar o submodule `backend` que está em um repositório privado.

## 📋 Solução: Personal Access Token (PAT)

### Passo 1: Criar Personal Access Token no GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token"** → **"Generate new token (classic)"**
3. Configure:
   - **Note**: "Netlify Build Access"
   - **Expiration**: Escolha uma data (recomendado: 1 ano)
   - **Scopes**: Marque `repo` (isso dará acesso a repositórios privados)
4. Clique em **"Generate token"**
5. **COPIE O TOKEN** (você só verá ele uma vez!)

### Passo 2: Configurar no Netlify

1. Acesse o painel do Netlify
2. Vá em **Site settings** → **Build & deploy** → **Environment variables**
3. Adicione a variável:
   - **Key**: `GITHUB_TOKEN`
   - **Value**: Cole o token que você copiou
4. Clique em **Save**

### Passo 3: Configurar o Build Command

No Netlify, vá em **Site settings** → **Build & deploy** → **Build settings**:

**Build command:**
```bash
git submodule update --init --recursive && cd frontend && npm ci && npm run build
```

Ou, se preferir usar o `netlify.toml`, atualize o arquivo conforme mostrado abaixo.

## 🔄 Alternativa: Atualizar netlify.toml

Se preferir configurar via arquivo, atualize o `netlify.toml`:

```toml
[build]
  base = "frontend"
  command = "git submodule update --init --recursive && npm ci && npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"
  NPM_CONFIG_PRODUCTION = "false"
  SECRETS_SCAN_OMIT_KEYS = "VITE_API_URL,VITE_SUPABASE_URL,VITE_SUPABASE_ANON_KEY,API_BASE_URL"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Importante**: O comando `git submodule update --init --recursive` precisa ser executado ANTES do `npm ci`.

## ✅ Verificação

Após configurar:

1. Faça um novo deploy (ou aguarde o próximo push)
2. Verifique os logs do build no Netlify
3. O submodule deve ser clonado com sucesso

## 🚨 Se ainda não funcionar

Se ainda houver problemas:

1. Verifique se o token tem permissão `repo`
2. Verifique se o repositório `CRQExecComMgmtBackend` está acessível
3. Tente fazer um deploy manual no Netlify para ver os logs completos

## 📝 Nota sobre Segurança

- O token `GITHUB_TOKEN` é usado apenas durante o build
- Não é exposto no código do frontend
- Mantenha o token seguro e não o compartilhe
