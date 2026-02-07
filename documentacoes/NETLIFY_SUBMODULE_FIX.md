# 🔧 Solução para Erro de Submódulo no Netlify

O Netlify está tentando clonar o submódulo `backend` durante o deploy, causando falha no build. Este documento explica como resolver o problema.

## ⚠️ Problema

O Netlify tenta clonar submódulos durante a fase de "preparing repo", antes mesmo do build começar. Isso causa erro quando o repositório do submódulo é privado ou requer autenticação.

## ✅ Solução

### Opção 1: Configurar no Painel do Netlify (Recomendado)

1. Acesse o painel do Netlify: https://app.netlify.com
2. Vá em **Site settings** > **Build & deploy** > **Environment variables**
3. Adicione as seguintes variáveis:
   - **Key**: `GIT_SUBMODULE_UPDATE`
   - **Value**: `false`
   - **Key**: `GIT_SUBMODULE_STRATEGY`
   - **Value**: `none`

4. Salve as alterações
5. Faça um novo deploy

### Opção 2: Usar Build Settings no Painel

1. Acesse o painel do Netlify
2. Vá em **Site settings** > **Build & deploy** > **Build settings**
3. Em **Build command**, adicione antes do comando:
   ```bash
   git config --global submodule.recurse false && git config --global submodule.active false && 
   ```
   
   O comando completo deve ficar:
   ```bash
   git config --global submodule.recurse false && git config --global submodule.active false && npm ci && npm run build
   ```

### Opção 3: Remover .gitmodules Temporariamente (Não Recomendado)

Se as opções acima não funcionarem, você pode remover o `.gitmodules` antes do deploy e depois restaurá-lo:

```bash
# Antes do deploy
git mv .gitmodules .gitmodules.bak
git commit -m "Temporariamente removendo .gitmodules para deploy no Netlify"
git push

# Após o deploy, restaurar
git mv .gitmodules.bak .gitmodules
git commit -m "Restaurando .gitmodules"
git push
```

**⚠️ Atenção**: Esta opção não é recomendada porque você perderá a capacidade de fazer commits no backend via este projeto.

## 🔍 Verificação

Após configurar, verifique os logs do Netlify. Você não deve mais ver erros relacionados a submódulos.

## 📝 Notas

- O arquivo `.netlify/state.json` foi criado para tentar desabilitar submódulos, mas pode não funcionar em todas as versões do Netlify
- A melhor solução é configurar no painel do Netlify (Opção 1)
- O backend não é necessário para o build do frontend, apenas para desenvolvimento local

## 🔗 Referências

- [Netlify Build Settings](https://docs.netlify.com/configure-builds/overview/)
- [Git Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
