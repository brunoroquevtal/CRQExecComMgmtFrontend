# 🚀 Configuração de Deploy

Guia para configurar o frontend e backend em produção.

## 📍 URLs de Produção

- **Backend:** https://crqcommunidationbackend.netlify.app/
- **Frontend:** (configure após deploy)

## 🔧 Configuração do Frontend

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto frontend:

```env
VITE_API_URL=https://crqcommunidationbackend.netlify.app/api
```

### 2. Build para Produção

```bash
cd frontend
npm run build
```

O build será gerado na pasta `dist/`.

### 3. Deploy no Netlify

1. Acesse o Netlify Dashboard
2. Conecte o repositório do frontend
3. Configure:
   - **Build command:** `cd frontend && npm run build`
   - **Publish directory:** `frontend/dist`
   - **Environment variables:**
     - `VITE_API_URL` = `https://crqcommunidationbackend.netlify.app/api`

## ⚠️ Importante sobre o Backend no Netlify

O Netlify é uma plataforma de hospedagem estática. Para uma API Express, você tem algumas opções:

### Opção 1: Netlify Functions (Recomendado)

Se você configurou o backend como Netlify Functions, a URL deve ser:
```
https://crqcommunidationbackend.netlify.app/.netlify/functions/api
```

### Opção 2: Backend em outra plataforma

Para uma API Express completa, considere usar:
- **Railway** (https://railway.app) - Gratuito para começar
- **Render** (https://render.com) - Gratuito com limitações
- **Heroku** (https://heroku.com) - Pago
- **Vercel** (https://vercel.com) - Serverless functions

### Opção 3: Verificar configuração atual

Se o backend está funcionando em `https://crqcommunidationbackend.netlify.app/`, verifique:

1. Se está usando Netlify Functions
2. Se a URL base está correta
3. Se os endpoints estão acessíveis

## 🧪 Testar o Backend Deployado

### Health Check

```bash
curl https://crqcommunidationbackend.netlify.app/health
```

### Informações da API

```bash
curl https://crqcommunidationbackend.netlify.app/
```

### Listar Atividades

```bash
curl https://crqcommunidationbackend.netlify.app/api/activities
```

## 🔍 Troubleshooting

### Erro: CORS

Se houver erros de CORS, configure no backend:

```javascript
app.use(cors({
  origin: ['https://seu-frontend.netlify.app', 'http://localhost:5173'],
  credentials: true
}));
```

### Erro: 404 Not Found

- Verifique se a URL do backend está correta
- Verifique se os endpoints estão acessíveis
- Verifique se o Netlify Functions está configurado corretamente

### Erro: Timeout

- Aumente o timeout no frontend (já configurado para 5 minutos)
- Verifique se o Netlify Functions tem timeout suficiente

## 📝 Checklist de Deploy

- [ ] Backend deployado e acessível
- [ ] Frontend configurado com `VITE_API_URL` correto
- [ ] CORS configurado no backend
- [ ] Variáveis de ambiente configuradas no Netlify
- [ ] Build do frontend gerado com sucesso
- [ ] Testes realizados em produção
