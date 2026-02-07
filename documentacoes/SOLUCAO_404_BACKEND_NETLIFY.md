# 🔧 Solução: Erro 404 no Backend Netlify

## ⚠️ Problema

O endpoint `/api/auth/profile` está retornando 404 no backend do Netlify:
```
crqcommunidationbackend.netlify.app/api/auth/profile:1  Failed to load resource: the server responded with a status of 404 (Not Found)
```

## 🔍 Causa

O backend Express não está configurado corretamente no Netlify. O Netlify é uma plataforma de hospedagem estática e precisa de configuração especial para APIs Express.

## ✅ Soluções

### Opção 1: Configurar Netlify Functions (Recomendado se backend está no Netlify)

Se o backend está no mesmo repositório ou no Netlify, você precisa configurar Netlify Functions:

#### 1. Criar arquivo `netlify/functions/api.js` no backend:

```javascript
const serverless = require('serverless-http');
const app = require('../server.js');

module.exports.handler = serverless(app);
```

#### 2. Criar `netlify.toml` na raiz do backend:

```toml
[build]
  functions = "netlify/functions"
  command = "npm install"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
```

#### 3. Atualizar URL no frontend:

No Netlify Dashboard do frontend, configure:
```
VITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api
```

### Opção 2: Backend em Repositório Separado (Recomendado)

Se o backend está em um repositório separado, você tem duas opções:

#### A. Deploy em Railway (Gratuito e Fácil)

1. Acesse: https://railway.app
2. Conecte o repositório do backend
3. Railway detecta automaticamente Node.js
4. Configure variáveis de ambiente:
   - `PORT` (Railway define automaticamente)
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
5. A URL será: `https://seu-backend.up.railway.app`

#### B. Deploy em Render (Gratuito)

1. Acesse: https://render.com
2. Crie um novo "Web Service"
3. Conecte o repositório do backend
4. Configure:
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Port:** `3000`
5. A URL será: `https://seu-backend.onrender.com`

### Opção 3: Verificar Configuração Atual

Se o backend já está no Netlify, verifique:

1. **URL correta do backend:**
   - Teste: `https://crqcommunidationbackend.netlify.app/health`
   - Teste: `https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health`

2. **Configuração no Netlify Dashboard:**
   - Site settings → Build & deploy
   - Verifique se o build command está correto
   - Verifique se as variáveis de ambiente estão configuradas

3. **Logs do Netlify:**
   - Dashboard → Deploys → Ver logs do último deploy
   - Procure por erros de build ou runtime

## 🔧 Correção Rápida (Frontend)

Enquanto o backend não está funcionando, o frontend já tem fallback para buscar diretamente do Supabase. Mas para corrigir completamente:

### 1. Verificar URL do Backend

No Netlify Dashboard do frontend, verifique se `VITE_API_URL` está configurada corretamente:

- Se backend usa Netlify Functions:
  ```
  VITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api
  ```

- Se backend está em outra plataforma:
  ```
  VITE_API_URL=https://seu-backend.up.railway.app/api
  ```

### 2. Testar Endpoints

Teste manualmente no navegador ou com curl:

```bash
# Health check
curl https://crqcommunidationbackend.netlify.app/health

# Com Netlify Functions
curl https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health
```

## 📝 Checklist

- [ ] Backend está deployado e acessível
- [ ] URL do backend está correta no frontend (`VITE_API_URL`)
- [ ] CORS está configurado no backend para aceitar requisições do frontend
- [ ] Variáveis de ambiente estão configuradas no backend
- [ ] Logs do backend não mostram erros
- [ ] Frontend está fazendo requisições para a URL correta

## 🆘 Próximos Passos

1. **Identificar onde o backend está deployado:**
   - Verifique se está no Netlify (mesmo site ou separado)
   - Verifique se está em outra plataforma (Railway, Render, etc.)

2. **Configurar corretamente:**
   - Se no Netlify: configurar Netlify Functions
   - Se em outra plataforma: verificar URL e variáveis de ambiente

3. **Atualizar frontend:**
   - Configurar `VITE_API_URL` correta no Netlify Dashboard
   - Fazer novo deploy do frontend

## 💡 Recomendação

Para uma API Express completa, recomendo usar **Railway** ou **Render** em vez do Netlify, pois:
- São mais fáceis de configurar
- Não têm limitações de timeout (Netlify Functions tem limite de 10-26s)
- Suportam melhor aplicações Express completas
- Têm planos gratuitos generosos
