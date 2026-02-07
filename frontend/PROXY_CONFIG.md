# 🔄 Configuração do Proxy Vite

## 📋 Como Funciona

O proxy do Vite é usado **apenas quando `VITE_API_URL` não está definida**.

### Cenário 1: Sem VITE_API_URL (Proxy Ativo)

```env
# .env.local não existe ou VITE_API_URL não está definida
```

**Comportamento:**
- Requisições para `/api/*` são redirecionadas para `http://localhost:3000`
- Exemplo: `GET /api/statistics` → `http://localhost:3000/api/statistics`
- **Útil para desenvolvimento local** quando o backend está rodando em `localhost:3000`

### Cenário 2: Com VITE_API_URL (Proxy Ignorado)

```env
# .env.local
VITE_API_URL=https://crqcommunidationbackend.netlify.app/api
```

**Comportamento:**
- O axios usa a URL completa diretamente
- Exemplo: `GET /api/statistics` → `https://crqcommunidationbackend.netlify.app/api/statistics`
- O proxy **não é usado** porque a URL é absoluta
- **Útil para desenvolvimento com backend remoto** (Netlify, etc.)

## 🔧 Configuração Atual

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:3000',  // Backend local
    changeOrigin: true,
    secure: false
  }
}
```

## 📊 Fluxo de Decisão

```
Requisição: api.get('/statistics')
    ↓
Verifica: VITE_API_URL está definida?
    ↓
    ├─ SIM → Usa URL completa (ignora proxy)
    │         https://crqcommunidationbackend.netlify.app/api/statistics
    │
    └─ NÃO → Usa proxy (URL relativa)
              /api/statistics → http://localhost:3000/api/statistics
```

## 🎯 Quando Usar Cada Opção

### Usar Proxy (sem VITE_API_URL)
- ✅ Backend rodando localmente em `localhost:3000`
- ✅ Desenvolvimento rápido sem configurar variáveis
- ✅ Testes locais

### Usar VITE_API_URL
- ✅ Backend no Netlify, Railway, Render, etc.
- ✅ Backend em outro servidor/porta
- ✅ Produção ou staging

## 🔍 Verificar Qual Está Sendo Usado

1. Abra o DevTools (F12)
2. Vá na aba **Network**
3. Faça uma requisição (ex: carregar dashboard)
4. Veja a URL da requisição:
   - `http://localhost:5173/api/...` → Proxy ativo (redireciona para localhost:3000)
   - `https://crqcommunidationbackend.netlify.app/api/...` → VITE_API_URL definida

## ⚙️ Modificar o Proxy

Se você quiser mudar o target do proxy (ex: outra porta ou servidor):

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:4000',  // Outra porta
    // ou
    target: 'http://192.168.1.100:3000',  // Outro servidor na rede
    changeOrigin: true,
    secure: false
  }
}
```

## 📝 Notas Importantes

1. **O proxy só funciona em desenvolvimento** (`npm run dev`)
2. **Em produção** (`npm run build`), sempre use `VITE_API_URL`
3. **O proxy não funciona com URLs absolutas** - se `VITE_API_URL` estiver definida, o axios usa ela diretamente
4. **Reinicie o servidor** após alterar `vite.config.js`
