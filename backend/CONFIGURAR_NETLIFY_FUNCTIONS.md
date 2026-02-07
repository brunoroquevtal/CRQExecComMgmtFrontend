# 🔧 Configurar Netlify Functions para o Backend

## 📋 Arquivos Criados

Os seguintes arquivos foram criados para configurar o Netlify Functions:

1. **`netlify/functions/api.js`** - Wrapper serverless para o Express
2. **`netlify.toml`** - Configuração do Netlify para o backend

## ✅ O que foi feito

### 1. Netlify Function (`netlify/functions/api.js`)

Este arquivo converte o servidor Express em uma Netlify Function usando `serverless-http`:

```javascript
const serverless = require('serverless-http');
const app = require('../../server.js');
module.exports.handler = serverless(app);
```

### 2. Configuração Netlify (`netlify.toml`)

Este arquivo configura:
- Diretório das functions: `netlify/functions`
- Redirects para `/api/*` → `/.netlify/functions/api/:splat`
- Redirects para `/*` → `/.netlify/functions/api/:splat`

## 🚀 Próximos Passos

### 1. Verificar se o backend está no Netlify

Se o backend está em um repositório separado no Netlify:

1. Acesse o Netlify Dashboard do backend
2. Verifique se o `netlify.toml` está na raiz do repositório
3. Verifique se a estrutura de pastas está correta:
   ```
   backend/
   ├── netlify.toml
   ├── netlify/
   │   └── functions/
   │       └── api.js
   ├── server.js
   └── ...
   ```

### 2. Configurar Variáveis de Ambiente no Netlify

No Netlify Dashboard do backend, configure:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_EMAIL_DOMAINS` (opcional)
- `API_DEBUG` (opcional)

### 3. Atualizar URL no Frontend

No Netlify Dashboard do frontend, atualize `VITE_API_URL`:

```
VITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api
```

**Importante:** Note o `.netlify/functions/api` no final da URL!

### 4. Fazer Deploy

Após configurar:

1. Faça commit e push dos arquivos no repositório do backend
2. O Netlify fará deploy automático
3. Teste o endpoint: `https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health`

## 🧪 Testar

Após o deploy, teste:

```bash
# Health check
curl https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health

# Profile (com token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://crqcommunidationbackend.netlify.app/.netlify/functions/api/auth/profile
```

## ⚠️ Limitações do Netlify Functions

- **Timeout:** 10 segundos (free) ou 26 segundos (pro)
- **Payload:** 6MB (free) ou 6MB (pro)
- **Memória:** 128MB (free) ou 1024MB (pro)

Se você precisar de mais recursos, considere usar Railway ou Render.

## 🔄 Alternativa: Railway ou Render

Se o Netlify Functions não atender suas necessidades:

### Railway (Recomendado)
1. Acesse: https://railway.app
2. Conecte o repositório do backend
3. Railway detecta automaticamente Node.js
4. Configure variáveis de ambiente
5. URL será: `https://seu-backend.up.railway.app`

### Render
1. Acesse: https://render.com
2. Crie um "Web Service"
3. Conecte o repositório
4. Configure build e start commands
5. URL será: `https://seu-backend.onrender.com`

## 📝 Notas

- O `serverless-http` já está instalado no `package.json`
- O `netlify.toml` deve estar na raiz do repositório do backend
- Os redirects garantem que todas as rotas funcionem corretamente
