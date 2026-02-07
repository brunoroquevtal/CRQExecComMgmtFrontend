# 📝 Como Fazer Commit do Backend via Este Projeto

Este documento explica como fazer commits do backend que está configurado como submódulo Git neste projeto.

## 🔧 Configuração Atual

- O backend está configurado como um **git submodule** em `backend/`
- Você pode fazer commits do backend via este projeto
- O Netlify **não** tentará buscar o submódulo durante o deploy do frontend

## 📋 Comandos Úteis

### Inicializar o Submódulo (primeira vez)

Se você acabou de clonar o repositório e o backend ainda não foi inicializado:

```bash
git submodule update --init --recursive
```

### Fazer Commit de Mudanças no Backend

1. **Navegue para o diretório do backend:**
   ```bash
   cd backend
   ```

2. **Verifique o status:**
   ```bash
   git status
   ```

3. **Adicione as mudanças:**
   ```bash
   git add .
   ```

4. **Faça o commit:**
   ```bash
   git commit -m "Descrição das mudanças"
   ```

5. **Faça push para o repositório do backend:**
   ```bash
   git push origin main
   # ou
   git push origin master
   ```

6. **Volte para a raiz do projeto:**
   ```bash
   cd ..
   ```

7. **Atualize a referência do submódulo no projeto principal:**
   ```bash
   git add backend
   git commit -m "Atualizar referência do backend"
   git push
   ```

### Atualizar o Backend para a Última Versão

Se o backend foi atualizado no repositório remoto:

```bash
cd backend
git pull origin main
cd ..
git add backend
git commit -m "Atualizar backend para última versão"
git push
```

### Verificar Status do Submódulo

Para ver se o submódulo está atualizado:

```bash
git submodule status
```

## ⚠️ Importante

### No Deploy do Frontend (Netlify)

- O Netlify **não** tentará buscar o submódulo durante o build
- A variável `GIT_SUBMODULE_UPDATE = "false"` está configurada no `netlify.toml`
- O frontend não precisa do código do backend para fazer o build
- O frontend se comunica com o backend apenas via API HTTP

### Estrutura do Repositório

```
CRQExecComMgmtFrontend/
├── frontend/          # Código do frontend
├── backend/           # Submódulo Git do backend
├── .gitmodules        # Configuração do submódulo
└── netlify.toml       # Configuração do Netlify (não busca submodules)
```

## 🔍 Troubleshooting

### Erro: "fatal: not a git repository"

Se você receber este erro ao tentar fazer commit no backend:

```bash
cd backend
git init  # Apenas se o backend não for um submódulo ainda
# Ou
git submodule update --init --recursive
```

### Backend não aparece como submódulo

Se o backend não estiver configurado como submódulo:

```bash
# Remover o diretório backend (se existir)
rm -rf backend

# Adicionar como submódulo
git submodule add https://github.com/brunoroquevtal/CRQExecComMgmtBackend.git backend

# Inicializar
git submodule update --init --recursive
```

### Verificar se está configurado corretamente

```bash
# Verificar se o .gitmodules existe
cat .gitmodules

# Verificar status do submódulo
git submodule status
```

## 📚 Referências

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [Netlify Build Configuration](https://docs.netlify.com/configure-builds/file-based-configuration/)
