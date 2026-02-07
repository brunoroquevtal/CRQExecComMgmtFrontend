# 🚀 Início Rápido - Versão Node.js/React

## ✅ Instalação Concluída

As dependências do frontend e backend foram instaladas com sucesso!

## 🎯 Como Iniciar a Aplicação

### Opção 1: Script PowerShell (Recomendado - Windows)

```powershell
.\start_nodejs.ps1
```

Este script iniciará automaticamente:
- Backend na porta 3000
- Frontend na porta 5173

### Opção 2: Manual (2 terminais)

**Terminal 1 - Backend:**
```powershell
cd backend
npm start
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

## 🌐 Acessar a Aplicação

Após iniciar, acesse:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000

## 🔐 Credenciais de Teste

- **Admin**: `admin` / `admin123`
- **Líder**: `lider` / `lider123`
- **Visualizador**: `visualizador` / `view123`

## 📝 Notas

- O banco de dados SQLite (`db/activity_control.db`) é compartilhado com a versão Python
- Se precisar restaurar a versão Python, os arquivos estão em `backup_python/`

## ⚠️ Problemas Comuns

### Erro de Política de Execução do PowerShell

Se encontrar erro ao executar scripts PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Ou use o CMD ao invés do PowerShell.

### Porta já em uso

Se a porta 3000 ou 5173 estiver em uso:

1. Altere a porta no arquivo `.env` do backend
2. Ou altere em `vite.config.js` do frontend

## 📚 Documentação

- `README_NODEJS.md` - Documentação completa
- `MIGRACAO_NODEJS.md` - Guia de migração
