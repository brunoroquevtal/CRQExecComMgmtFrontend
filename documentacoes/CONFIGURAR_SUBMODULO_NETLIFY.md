# 🔧 Configurar Submódulo Backend no Netlify

## ⚠️ Problema

O Netlify está tentando clonar o submódulo `backend` durante o deploy, causando falha no build:

```
Error checking out submodules: Submodule 'backend' registered for path 'backend'
fatal: could not read Username for 'https://github.com': No such device or address
```

## ✅ Solução: Configurar no Painel do Netlify

O Netlify tenta fazer checkout dos submódulos **durante a fase de preparação do repositório**, ANTES do build command ser executado. Por isso, precisamos configurar no painel do Netlify.

### Passo 1: Acessar Configurações do Site

1. Acesse o painel do Netlify: https://app.netlify.com
2. Selecione seu site (frontend)
3. Vá em **Site settings** → **Build & deploy** → **Environment variables**

### Passo 2: Adicionar Variáveis de Ambiente

Adicione as seguintes variáveis de ambiente:

| Key | Value |
|-----|-------|
| `GIT_SUBMODULE_UPDATE` | `false` |
| `GIT_SUBMODULE_STRATEGY` | `none` |

**Como adicionar:**
1. Clique em **"Add variable"**
2. Digite o **Key** e o **Value**
3. Clique em **"Save"**
4. Repita para a segunda variável

### Passo 3: Fazer Novo Deploy

Após adicionar as variáveis:
1. Vá em **Deploys** no menu lateral
2. Clique em **"Trigger deploy"** → **"Clear cache and deploy site"**
3. Aguarde o deploy completar

## 🔍 Verificação

Após configurar, verifique os logs do deploy. Você não deve mais ver erros relacionados a submódulos.

Os logs devem mostrar algo como:
```
✓ Preparing repo
✓ Building site
✓ Deploying site
```

## 📝 Por que isso funciona?

- `GIT_SUBMODULE_UPDATE=false`: Desabilita completamente a atualização de submódulos
- `GIT_SUBMODULE_STRATEGY=none`: Define estratégia para não clonar submódulos

Essas variáveis são lidas pelo Netlify **antes** do checkout do repositório, então evitam que o Netlify tente clonar o submódulo.

## 🔄 Manter Submódulo para Commits Locais

Mesmo com essas configurações, você ainda pode:
- ✅ Fazer commits no backend a partir deste projeto localmente
- ✅ Usar `git submodule update --init` localmente quando necessário
- ✅ Fazer push de mudanças no backend via este projeto

O Netlify apenas não tentará clonar o submódulo durante o deploy.

## 🚨 Se ainda não funcionar

Se após configurar as variáveis o problema persistir:

1. **Verifique se as variáveis foram salvas corretamente:**
   - Volte em **Environment variables** e confirme que estão lá

2. **Limpe o cache do Netlify:**
   - **Deploys** → **Trigger deploy** → **"Clear cache and deploy site"**

3. **Verifique os logs completos:**
   - Abra o deploy que falhou
   - Procure por mensagens relacionadas a submódulos

4. **Alternativa: Usar Personal Access Token (se backend for privado):**
   - Se o repositório do backend for privado, você pode precisar de um token
   - Veja: `CONFIGURAR_SUBMODULE_NETLIFY.md` (documentação antiga)

## 📚 Referências

- [Netlify Build Environment Variables](https://docs.netlify.com/configure-builds/environment-variables/)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
