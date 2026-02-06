# 🚀 Guia de Deploy no Netlify

Este guia explica como fazer o deploy da aplicação no Netlify.

## 📋 Pré-requisitos

1. Conta no Netlify
2. Repositório no GitHub conectado ao Netlify
3. Backend Node.js rodando (pode ser em outro serviço como Heroku, Railway, etc.)

## 🔧 Configuração do Netlify

### 1. Arquivos de Configuração

Os seguintes arquivos já foram criados:

- **`netlify.toml`** - Configuração principal do Netlify
- **`frontend/public/_redirects`** - Redirecionamento de rotas para SPA
- **`frontend/src/utils/api.js`** - Utilitário de API com suporte a variáveis de ambiente

### 2. Configuração no Painel do Netlify

1. Acesse o painel do Netlify
2. Vá em **Site settings** > **Build & deploy**
3. Configure:
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/dist`
   - **Base directory**: (deixe vazio ou `/`)

### 3. Variáveis de Ambiente

No painel do Netlify, vá em **Site settings** > **Environment variables** e adicione:

- **`VITE_API_URL`**: URL completa do seu backend
  - Exemplo: `https://seu-backend.herokuapp.com/api`
  - Ou: `http://localhost:3000/api` (se backend estiver local)
  - **Importante**: Se não definir, usará `/api` (relativo ao domínio atual)

### 4. Deploy Automático

O Netlify fará deploy automático quando você fizer push para a branch principal do GitHub.

## 🔍 Verificação

Após o deploy:

1. Acesse a URL do seu site no Netlify
2. Verifique se a página de login carrega corretamente
3. Teste o login e navegação entre páginas
4. Verifique se as chamadas de API estão funcionando (abra o DevTools > Network)

## 🐛 Solução de Problemas

### Página de login não carrega

- Verifique se o arquivo `frontend/public/_redirects` existe
- Verifique se o `netlify.toml` está na raiz do repositório
- Verifique os logs de build no Netlify

### Erro 404 em rotas

- Certifique-se de que o arquivo `_redirects` contém: `/*    /index.html   200`
- Faça um novo deploy após adicionar o arquivo

### Erros de CORS ou API não conecta

- Verifique se a variável `VITE_API_URL` está configurada corretamente
- Verifique se o backend está rodando e acessível
- Verifique se o backend permite requisições do domínio do Netlify (CORS)

### Build falha

- Verifique os logs de build no Netlify
- Certifique-se de que todas as dependências estão no `package.json`
- Verifique se o Node.js está na versão correta (Netlify usa Node 18 por padrão)

## 📝 Notas Importantes

1. **Backend separado**: O frontend no Netlify precisa de um backend rodando em outro serviço
2. **Variáveis de ambiente**: Variáveis que começam com `VITE_` são expostas no frontend
3. **HTTPS**: O Netlify fornece HTTPS automaticamente
4. **Cache**: O Netlify faz cache automático. Se precisar limpar, use "Clear cache and deploy site"

## 🔄 Atualizações

Para atualizar a aplicação:

1. Faça as alterações no código
2. Commit e push para o GitHub
3. O Netlify fará deploy automático
4. Aguarde alguns minutos para o deploy completar

## 📚 Recursos

- [Documentação do Netlify](https://docs.netlify.com/)
- [Netlify Redirects](https://docs.netlify.com/routing/redirects/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
