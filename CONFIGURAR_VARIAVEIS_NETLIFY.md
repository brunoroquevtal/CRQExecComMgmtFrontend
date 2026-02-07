# 🔧 Configurar Variáveis de Ambiente no Netlify

## 📋 Variáveis Necessárias

Configure estas variáveis no **Netlify Dashboard** para o build funcionar corretamente:

### Variáveis Obrigatórias

1. **`VITE_API_URL`**
   - **Valor**: `https://crqcommunidationbackend.netlify.app/api`
   - **Descrição**: URL do backend no Netlify

### Variáveis Opcionais (para autenticação)

2. **`VITE_SUPABASE_URL`** (Opcional)
   - **Valor**: `https://seu-projeto.supabase.co`
   - **Descrição**: URL do projeto Supabase

3. **`VITE_SUPABASE_ANON_KEY`** (Opcional)
   - **Valor**: `sua-chave-anon-aqui`
   - **Descrição**: Chave anônima do Supabase (pública, pode estar no código)

## 🔧 Como Configurar no Netlify

### Passo 1: Acessar o Netlify Dashboard

1. Acesse: https://app.netlify.com
2. Selecione seu site
3. Vá em **Site settings** → **Environment variables**

### Passo 2: Adicionar Variáveis

Para cada variável:

1. Clique em **Add a variable**
2. Digite o **Key** (nome da variável)
3. Digite o **Value** (valor)
4. Selecione o **Scope**:
   - **All scopes** - Para produção, deploy previews e branch deploys
   - **Production** - Apenas para produção
   - **Deploy previews** - Apenas para previews
   - **Branch deploys** - Apenas para branches
5. Clique em **Save**

### Passo 3: Verificar

Após adicionar as variáveis:

1. Vá em **Deploys**
2. Clique em **Trigger deploy** → **Deploy site**
3. O build deve usar as variáveis configuradas

## ⚠️ Importante

- **NÃO** commite arquivos `.env` ou `.env.local` no git
- Esses arquivos já estão no `.gitignore`
- Use apenas variáveis de ambiente do Netlify para produção
- Para desenvolvimento local, use `.env.local` (não commitado)

## 📝 Variáveis Configuradas

Após configurar, você deve ter:

```
VITE_API_URL = https://crqcommunidationbackend.netlify.app/api
VITE_SUPABASE_URL = https://seu-projeto.supabase.co (opcional)
VITE_SUPABASE_ANON_KEY = sua-chave-anon (opcional)
```

## 🔍 Verificar se Está Funcionando

Após o deploy:

1. Abra o site no navegador
2. Abra o DevTools (F12) → Console
3. O código deve usar as variáveis configuradas
4. As requisições devem ir para a URL correta do backend

## 🐛 Problemas Comuns

### Build falha com "secrets detected"

**Solução**: Certifique-se de que:
- Nenhum arquivo `.env` está commitado
- As variáveis estão configuradas no Netlify Dashboard
- Não há valores hardcoded no código

### Variáveis não funcionam

**Solução**:
1. Verifique se as variáveis estão configuradas no Netlify
2. Verifique se o nome está correto (case-sensitive)
3. Faça um novo deploy após adicionar variáveis
4. Variáveis `VITE_*` são substituídas no build, não em runtime

### Variáveis aparecem como undefined

**Solução**:
- Variáveis devem começar com `VITE_` para serem expostas no frontend
- Reinicie o servidor de desenvolvimento após criar `.env.local`
- No Netlify, faça um novo deploy após adicionar variáveis
