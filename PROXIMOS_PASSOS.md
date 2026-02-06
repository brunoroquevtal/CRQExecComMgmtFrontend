# 📋 Próximos Passos - Separação de Repositórios

## ✅ O que já foi feito:

1. ✅ Backend copiado para: `C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtBackend`
2. ✅ `.gitignore` do frontend atualizado (exclui pasta `backend/`)
3. ✅ `README.md` do frontend atualizado
4. ✅ `README.md` e `.gitignore` do backend criados
5. ✅ Repositórios Git inicializados em ambos os diretórios

## 🔧 O que precisa fazer agora:

### Passo 1: Instalar Git

**Opção A - Via winget (recomendado):**
```powershell
winget install --id Git.Git -e --source winget
```

**Opção B - Download manual:**
1. Acesse: https://git-scm.com/download/win
2. Baixe e instale
3. **IMPORTANTE:** Durante a instalação, marque "Add Git to PATH"

**Após instalar:**
- Feche e abra novamente o PowerShell
- Teste com: `git --version`

### Passo 2: Criar repositórios no GitHub

**Opção A - Via GitHub CLI (se tiver instalado):**
```powershell
# Instalar GitHub CLI
winget install --id GitHub.cli

# Autenticar
gh auth login

# Criar repositórios
cd "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtBackend"
gh repo create CRQExecComMgmtBackend --private --source=. --remote=origin --push

cd "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtFrontend"
gh repo create CRQExecComMgmtFrontend --private --source=. --remote=origin --push
```

**Opção B - Manualmente (via site):**
1. Acesse: https://github.com/new
2. Crie o repositório `CRQExecComMgmtBackend` (privado)
3. Crie o repositório `CRQExecComMgmtFrontend` (privado)
4. **NÃO** inicialize com README, .gitignore ou license (já temos)

### Passo 3: Conectar e fazer push

**Backend:**
```powershell
cd "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtBackend"

# Adicionar remote (substitua SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/brunoroquevtal/CRQExecComMgmtBackend.git

# Verificar branch atual
git branch

# Renomear para main se necessário
git branch -M main

# Fazer push
git push -u origin main
```

**Frontend:**
```powershell
cd "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub\CRQExecComMgmtFrontend"

# Adicionar remote
git remote add origin https://github.com/brunoroquevtal/CRQExecComMgmtFrontend.git

# Adicionar mudanças (README.md e .gitignore atualizados)
git add .gitignore README.md

# Commit
git commit -m "Separar backend em repositório próprio"

# Verificar branch atual
git branch

# Renomear para main se necessário
git branch -M main

# Fazer push
git push -u origin main
```

### Passo 4: Configurar Git (se ainda não fez)

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
```

## 🚀 Script Automatizado

Execute o script `instalar-git-e-criar-repos.ps1` que foi criado anteriormente para automatizar todos os passos.

## ⚠️ Problemas Comuns

**Erro: "git não é reconhecido"**
- Git não está instalado ou não está no PATH
- Solução: Reinstale o Git e marque "Add to PATH"

**Erro: "remote origin already exists"**
- O remote já foi adicionado
- Solução: `git remote set-url origin https://github.com/brunoroquevtal/NOME_REPO.git`

**Erro de autenticação no push**
- Configure suas credenciais do GitHub
- Solução: Use GitHub CLI (`gh auth login`) ou configure token

## 📝 Notas Importantes

- A pasta `backend/` ainda existe no diretório do frontend, mas está sendo ignorada pelo `.gitignore`
- Você pode manter ela localmente ou deletá-la (não afetará o Git)
- Os dois repositórios são independentes agora
