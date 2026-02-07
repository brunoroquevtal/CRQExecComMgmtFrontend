# Script PowerShell para separar backend e frontend em repositórios diferentes

Write-Host "🚀 Separando repositórios..." -ForegroundColor Cyan

$basePath = "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub"
$frontendRepo = "$basePath\CRQExecComMgmtFrontend"
$backendRepo = "$basePath\CRQExecComMgmtBackend"

# Verificar se estamos no diretório correto
if (-not (Test-Path "$frontendRepo\backend")) {
    Write-Host "❌ Erro: Pasta backend não encontrada em $frontendRepo" -ForegroundColor Red
    Write-Host "   Execute este script a partir do diretório do projeto frontend" -ForegroundColor Yellow
    exit 1
}

# 1. Criar repositório do backend
Write-Host "`n📦 Criando repositório do backend..." -ForegroundColor Yellow
if (-not (Test-Path $backendRepo)) {
    New-Item -ItemType Directory -Path $backendRepo | Out-Null
    Write-Host "   ✓ Diretório criado: $backendRepo" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Diretório já existe: $backendRepo" -ForegroundColor Yellow
    $response = Read-Host "   Deseja continuar? Isso pode sobrescrever arquivos existentes (S/N)"
    if ($response -ne "S" -and $response -ne "s") {
        Write-Host "   Operação cancelada." -ForegroundColor Red
        exit 0
    }
}

# Copiar arquivos do backend
Write-Host "   Copiando arquivos do backend..." -ForegroundColor Gray
Copy-Item -Path "$frontendRepo\backend\*" -Destination $backendRepo -Recurse -Force -Exclude "node_modules"
Write-Host "   ✓ Arquivos copiados" -ForegroundColor Green

# Criar .gitignore para o backend se não existir
$backendGitignore = "$backendRepo\.gitignore"
if (-not (Test-Path $backendGitignore)) {
    Write-Host "   Criando .gitignore para o backend..." -ForegroundColor Gray
    @"
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json

# Environment
.env
.env.local
.env.*.local

# Database
*.db
*.db-journal
*.sqlite
*.sqlite3
db/activity_control.db

# Uploads
uploads/
uploads/*

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
*.tmp
*.temp
"@ | Out-File -FilePath $backendGitignore -Encoding UTF8
    Write-Host "   ✓ .gitignore criado" -ForegroundColor Green
}

# Criar README para o backend se não existir
$backendReadme = "$backendRepo\README.md"
if (-not (Test-Path $backendReadme)) {
    Write-Host "   Criando README para o backend..." -ForegroundColor Gray
    @"
# 🚀 CRQ Exec Com Mgmt - Backend API

Backend Node.js/Express para gerenciamento de janelas de mudança de TI.

## 📋 Instalação

\`\`\`bash
npm install
cp env.example .env
# Edite o arquivo .env com suas configurações
npm start
\`\`\`

## 🔧 Configuração

Edite o arquivo \`.env\` com suas configurações:

\`\`\`env
PORT=3000
API_DEBUG=false
API_BASE_URL=http://localhost:3000
\`\`\`

## 📡 Endpoints da API

- \`GET /health\` - Health check
- \`GET /\` - Informações da API
- \`POST /api/upload-excel\` - Upload de arquivo Excel
- \`GET /api/activities\` - Listar todas as atividades
- \`GET /api/activity/:sequencia/:seq\` - Obter atividade específica
- \`PUT /api/activity\` - Atualizar atividade
- \`GET /api/statistics\` - Obter estatísticas
- \`GET /api/message\` - Gerar mensagem de comunicação
- \`GET /api/message-detailed\` - Gerar mensagem detalhada
- \`DELETE /api/clear-database\` - Limpar base de dados

## 🛠️ Scripts Disponíveis

- \`npm start\` - Inicia o servidor em modo produção
- \`npm run dev\` - Inicia o servidor em modo desenvolvimento (com nodemon)

## 🔗 Frontend

O frontend está disponível em: [CRQExecComMgmtFrontend](https://github.com/SEU_USUARIO/CRQExecComMgmtFrontend)

## 📦 Dependências Principais

- \`express\` - Framework web
- \`sqlite3\` - Cliente SQLite
- \`xlsx\` - Processamento de Excel
- \`multer\` - Upload de arquivos
- \`cors\` - CORS middleware
- \`bcryptjs\` - Hash de senhas
- \`jsonwebtoken\` - Autenticação JWT

## 🔐 Autenticação

A API utiliza autenticação JWT. Configure as credenciais no arquivo \`.env\`.

## 📝 Notas

- O banco de dados SQLite é criado automaticamente na primeira execução
- Os arquivos Excel enviados são salvos na pasta \`uploads/\`
"@ | Out-File -FilePath $backendReadme -Encoding UTF8
    Write-Host "   ✓ README criado" -ForegroundColor Green
}

# Inicializar git no backend (se ainda não estiver inicializado)
Set-Location $backendRepo
if (-not (Test-Path ".git")) {
    Write-Host "   Inicializando repositório Git..." -ForegroundColor Gray
    git init
    git add .
    git commit -m "Initial commit: Backend separado do repositório principal"
    Write-Host "   ✓ Repositório Git inicializado" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Repositório Git já existe no backend" -ForegroundColor Yellow
}

Write-Host "`n✅ Backend preparado em: $backendRepo" -ForegroundColor Green

# 2. Preparar frontend
Write-Host "`n⚛️  Preparando repositório do frontend..." -ForegroundColor Yellow
Set-Location $frontendRepo

# Atualizar .gitignore para excluir backend
$frontendGitignore = "$frontendRepo\.gitignore"
$gitignoreContent = Get-Content $frontendGitignore -Raw -ErrorAction SilentlyContinue

if ($gitignoreContent -notmatch "backend/") {
    Write-Host "   Atualizando .gitignore para excluir backend..." -ForegroundColor Gray
    if ($gitignoreContent) {
        Add-Content -Path $frontendGitignore -Value "`n# Backend (repositório separado)`nbackend/"
    } else {
        @"
# Backend (repositório separado)
backend/
"@ | Out-File -FilePath $frontendGitignore -Encoding UTF8
    }
    Write-Host "   ✓ .gitignore atualizado" -ForegroundColor Green
} else {
    Write-Host "   ✓ .gitignore já contém exclusão do backend" -ForegroundColor Green
}

# Atualizar README do frontend
Write-Host "   Atualizando README do frontend..." -ForegroundColor Gray
$frontendReadme = @"
# 🎨 CRQ Exec Com Mgmt - Frontend

Frontend React para gerenciamento de janelas de mudança de TI.

## 📋 Instalação

\`\`\`bash
npm install
npm run dev
\`\`\`

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo \`.env\` na raiz do projeto frontend:

\`\`\`env
VITE_API_URL=http://localhost:3000/api
\`\`\`

**Nota:** Se não definir \`VITE_API_URL\`, o frontend usará \`/api\` como padrão (proxy do Vite).

### Proxy de Desenvolvimento

O Vite está configurado para fazer proxy das requisições \`/api\` para \`http://localhost:3000\` durante o desenvolvimento.

## 🚀 Scripts Disponíveis

- \`npm run dev\` - Inicia servidor de desenvolvimento
- \`npm run build\` - Gera build de produção
- \`npm run preview\` - Preview do build de produção

## 🎨 Funcionalidades

- **Dashboard**: Gráficos e indicadores em tempo real
- **Editor de Dados**: Edição de atividades
- **Comunicação**: Geração de mensagem de comunicação
- **Configurações**: Upload de Excel e limpeza de dados
- **Planejamento**: Visualização em Gantt

## 📦 Dependências Principais

- \`react\` - Biblioteca React
- \`react-router-dom\` - Roteamento
- \`axios\` - Cliente HTTP
- \`recharts\` - Gráficos
- \`react-hot-toast\` - Notificações
- \`tailwindcss\` - Framework CSS
- \`vite\` - Build tool

## 🔗 Backend

O backend está disponível em: [CRQExecComMgmtBackend](https://github.com/SEU_USUARIO/CRQExecComMgmtBackend)

## 📝 Notas

- O frontend se conecta ao backend através da API REST
- Certifique-se de que o backend está rodando antes de iniciar o frontend
- Para produção, configure a variável \`VITE_API_URL\` com a URL do backend em produção
"@

$frontendReadme | Out-File -FilePath "$frontendRepo\README.md" -Encoding UTF8
Write-Host "   ✓ README atualizado" -ForegroundColor Green

Write-Host "`n✅ Frontend preparado em: $frontendRepo" -ForegroundColor Green

# Resumo final
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Crie os repositórios no GitHub:" -ForegroundColor White
Write-Host "   - CRQExecComMgmtBackend" -ForegroundColor Gray
Write-Host "   - CRQExecComMgmtFrontend" -ForegroundColor Gray
Write-Host ""
Write-Host "2. No backend ($backendRepo):" -ForegroundColor White
Write-Host "   cd `"$backendRepo`"" -ForegroundColor Gray
Write-Host "   git remote add origin https://github.com/SEU_USUARIO/CRQExecComMgmtBackend.git" -ForegroundColor Gray
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "3. No frontend ($frontendRepo):" -ForegroundColor White
Write-Host "   cd `"$frontendRepo`"" -ForegroundColor Gray
Write-Host "   git add .gitignore README.md" -ForegroundColor Gray
Write-Host "   git commit -m `"Separar backend em repositório próprio`"" -ForegroundColor Gray
Write-Host "   git remote add origin https://github.com/SEU_USUARIO/CRQExecComMgmtFrontend.git" -ForegroundColor Gray
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Separação concluída!" -ForegroundColor Green
