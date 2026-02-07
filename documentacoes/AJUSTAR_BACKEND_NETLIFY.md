# 🔧 Ajustar Backend no Netlify

O backend retornou 404, o que indica que precisa ser configurado corretamente no Netlify.

## ⚠️ Problema Identificado

O Netlify é uma plataforma de hospedagem estática. Para uma API Express, você precisa usar **Netlify Functions**.

## 🔧 Solução: Configurar Netlify Functions

### Opção 1: Converter para Netlify Functions (Recomendado)

1. **Instalar dependências:**

```bash
cd CRQExecComMgmtBackend
npm install serverless-http
```

2. **Criar arquivo `netlify/functions/api.js`:**

```javascript
const serverless = require('serverless-http');
const app = require('../server.js');

module.exports.handler = serverless(app);
```

3. **Criar `netlify.toml` na raiz do backend:**

```toml
[build]
  functions = "netlify/functions"
  command = "echo 'No build needed'"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
```

### Opção 2: Usar outra plataforma (Mais fácil)

Para uma API Express completa, considere usar:

#### Railway (Recomendado - Gratuito)

1. Acesse: https://railway.app
2. Conecte seu repositório GitHub
3. Selecione o repositório do backend
4. Railway detecta automaticamente Node.js
5. Configure:
   - **Start Command:** `npm start`
   - **Port:** `3000` (ou use a variável `PORT`)

A URL será algo como: `https://seu-backend.up.railway.app`

#### Render (Gratuito)

1. Acesse: https://render.com
2. Crie um novo "Web Service"
3. Conecte o repositório do backend
4. Configure:
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`

#### Vercel (Serverless)

1. Acesse: https://vercel.com
2. Conecte o repositório
3. Vercel detecta automaticamente Express

## 🔍 Verificar URL Atual

Teste estas URLs para ver qual funciona:

```powershell
# Teste 1: URL raiz
Invoke-RestMethod -Uri "https://crqcommunidationbackend.netlify.app/"

# Teste 2: Health check
Invoke-RestMethod -Uri "https://crqcommunidationbackend.netlify.app/health"

# Teste 3: Netlify Functions
Invoke-RestMethod -Uri "https://crqcommunidationbackend.netlify.app/.netlify/functions/api/health"
```

## 📝 Configuração do Frontend

Depois de confirmar a URL correta do backend, atualize o frontend:

### Criar `.env` no frontend:

```env
VITE_API_URL=https://crqcommunidationbackend.netlify.app/api
```

Ou se usar Netlify Functions:

```env
VITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api
```

### Build e Deploy:

```bash
cd frontend
npm run build
```

## ✅ Checklist

- [ ] Backend configurado corretamente (Netlify Functions ou outra plataforma)
- [ ] URL do backend testada e funcionando
- [ ] Frontend configurado com `VITE_API_URL` correto
- [ ] CORS configurado no backend para aceitar requisições do frontend
- [ ] Build do frontend gerado
- [ ] Testes realizados em produção

## 🆘 Precisa de Ajuda?

Se o backend ainda não estiver funcionando, verifique:

1. **Logs do Netlify:** Dashboard > Deploys > Ver logs
2. **Configuração do Netlify:** Verifique `netlify.toml`
3. **Variáveis de ambiente:** Configure no Netlify Dashboard
4. **Timeout:** Netlify Functions tem limite de 10s (free) ou 26s (pro)
