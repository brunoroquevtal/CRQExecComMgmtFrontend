# Script para instalar Git e criar repositórios no GitHub
# Execute este script como Administrador para instalar o Git

param(
    [string]$GitHubUser = "brunoroquevtal"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Instalador de Git e Criador de Repositórios GitHub" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se um comando existe
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Função para adicionar Git ao PATH
function Add-GitToPath {
    $gitPaths = @(
        "C:\Program Files\Git\cmd",
        "C:\Program Files (x86)\Git\cmd",
        "$env:LOCALAPPDATA\Programs\Git\cmd"
    )
    
    foreach ($gitPath in $gitPaths) {
        if (Test-Path $gitPath) {
            if ($env:Path -notlike "*$gitPath*") {
                $env:Path += ";$gitPath"
                Write-Host "  Git adicionado ao PATH da sessao atual" -ForegroundColor Green
                return $true
            }
        }
    }
    return $false
}

# 1. Verificar e instalar Git
Write-Host "[1/5] Verificando instalacao do Git..." -ForegroundColor Yellow
if (Test-Command "git") {
    $gitVersion = git --version
    Write-Host "  [OK] Git ja esta instalado: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "  [INFO] Git nao encontrado. Tentando adicionar ao PATH..." -ForegroundColor Yellow
    if (Add-GitToPath) {
        if (Test-Command "git") {
            Write-Host "  [OK] Git encontrado e adicionado ao PATH" -ForegroundColor Green
        }
    }
    
    if (-not (Test-Command "git")) {
        Write-Host "  [INFO] Git nao encontrado. Instalando..." -ForegroundColor Yellow
        
        # Verificar se winget está disponível
        if (Test-Command "winget") {
            Write-Host "  Instalando Git via winget..." -ForegroundColor Gray
            winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
            
            # Tentar adicionar ao PATH novamente
            Start-Sleep -Seconds 2
            Add-GitToPath | Out-Null
            
            if (Test-Command "git") {
                Write-Host "  [OK] Git instalado e adicionado ao PATH" -ForegroundColor Green
            } else {
                Write-Host "  [AVISO] Git instalado mas nao encontrado no PATH." -ForegroundColor Yellow
                Write-Host "  Reinicie o PowerShell e execute novamente." -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "  [ERRO] winget nao encontrado. Instale Git manualmente:" -ForegroundColor Red
            Write-Host "  https://git-scm.com/download/win" -ForegroundColor Cyan
            Write-Host "  Apos instalar, reinicie o PowerShell e execute este script novamente." -ForegroundColor Yellow
            exit 1
        }
    }
}

# Verificar novamente após instalação
if (-not (Test-Command "git")) {
    Write-Host "  [ERRO] Git ainda nao esta disponivel. Reinicie o PowerShell e tente novamente." -ForegroundColor Red
    exit 1
}

# 2. Configurar variáveis
Write-Host "`n[2/5] Configurando variaveis..." -ForegroundColor Yellow
$basePath = "C:\Users\vt422276\OneDrive - V.tal\Documentos\GitHub"
$backendRepo = "$basePath\CRQExecComMgmtBackend"
$frontendRepo = "$basePath\CRQExecComMgmtFrontend"

Write-Host "  Usuario GitHub: $GitHubUser" -ForegroundColor Gray
Write-Host "  Backend: $backendRepo" -ForegroundColor Gray
Write-Host "  Frontend: $frontendRepo" -ForegroundColor Gray

# Verificar se os diretórios existem
if (-not (Test-Path $backendRepo)) {
    Write-Host "  [ERRO] Diretorio do backend nao encontrado: $backendRepo" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $frontendRepo)) {
    Write-Host "  [ERRO] Diretorio do frontend nao encontrado: $frontendRepo" -ForegroundColor Red
    exit 1
}

# 3. Verificar e configurar Git
Write-Host "`n[3/5] Verificando configuracao do Git..." -ForegroundColor Yellow
$gitUser = git config --global user.name 2>$null
$gitEmail = git config --global user.email 2>$null

if (-not $gitUser -or -not $gitEmail) {
    Write-Host "  [AVISO] Git nao esta configurado." -ForegroundColor Yellow
    Write-Host "  Configure suas credenciais:" -ForegroundColor Cyan
    $name = Read-Host "  Digite seu nome"
    $email = Read-Host "  Digite seu email"
    git config --global user.name $name
    git config --global user.email $email
    Write-Host "  [OK] Git configurado" -ForegroundColor Green
} else {
    Write-Host "  [OK] Git ja esta configurado: $gitUser <$gitEmail>" -ForegroundColor Green
}

# 4. Verificar GitHub CLI (opcional)
Write-Host "`n[4/5] Verificando GitHub CLI..." -ForegroundColor Yellow
$useGitHubCLI = $false
if (Test-Command "gh") {
    Write-Host "  [OK] GitHub CLI encontrado" -ForegroundColor Green
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Autenticado no GitHub" -ForegroundColor Green
        $useGitHubCLI = $true
    } else {
        Write-Host "  [INFO] Nao autenticado. Deseja fazer login? [S/N]" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq "S" -or $response -eq "s") {
            gh auth login
            $useGitHubCLI = $true
        }
    }
} else {
    Write-Host "  [INFO] GitHub CLI nao encontrado (opcional)" -ForegroundColor Yellow
    Write-Host "  Voce pode criar os repos manualmente ou instalar GitHub CLI" -ForegroundColor Gray
}

# 5. Criar repositórios e fazer push
Write-Host "`n[5/5] Criando repositorios e fazendo push..." -ForegroundColor Yellow

if ($useGitHubCLI) {
    # Usar GitHub CLI
    Write-Host "  Usando GitHub CLI para criar repositorios..." -ForegroundColor Gray
    
    # Backend
    Write-Host "  Criando repositorio CRQExecComMgmtBackend..." -ForegroundColor Gray
    Set-Location $backendRepo
    if (-not (Test-Path ".git")) {
        git init
        git add .
        git commit -m "Initial commit: Backend separado"
    }
    $existingRemote = git remote get-url origin -ErrorAction SilentlyContinue
    if (-not $existingRemote) {
        gh repo create CRQExecComMgmtBackend --private --source=. --remote=origin --push 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Backend criado e push realizado" -ForegroundColor Green
        } else {
            Write-Host "  [AVISO] Erro ao criar via CLI. Tente manualmente." -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [INFO] Remote ja existe. Fazendo push..." -ForegroundColor Gray
        git push -u origin main 2>&1 | Out-Null
    }
    
    # Frontend
    Write-Host "  Criando repositorio CRQExecComMgmtFrontend..." -ForegroundColor Gray
    Set-Location $frontendRepo
    $existingRemote = git remote get-url origin -ErrorAction SilentlyContinue
    if (-not $existingRemote) {
        gh repo create CRQExecComMgmtFrontend --private --source=. --remote=origin --push 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Frontend criado e push realizado" -ForegroundColor Green
        } else {
            Write-Host "  [AVISO] Erro ao criar via CLI. Tente manualmente." -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [INFO] Remote ja existe. Fazendo push..." -ForegroundColor Gray
        git push -u origin main 2>&1 | Out-Null
    }
} else {
    # Método manual
    Write-Host "  [INFO] Modo manual selecionado." -ForegroundColor Yellow
    Write-Host "  Por favor, crie os repositorios no GitHub primeiro:" -ForegroundColor Cyan
    Write-Host "  1. Acesse: https://github.com/new" -ForegroundColor White
    Write-Host "  2. Crie: CRQExecComMgmtBackend (privado)" -ForegroundColor White
    Write-Host "  3. Crie: CRQExecComMgmtFrontend (privado)" -ForegroundColor White
    Write-Host "  4. NAO inicialize com README, .gitignore ou license" -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "  Repositorios criados? Pressione Enter para continuar..."
    
    # Conectar backend
    Write-Host "  Conectando backend..." -ForegroundColor Gray
    Set-Location $backendRepo
    if (-not (Test-Path ".git")) {
        git init
        git add .
        git commit -m "Initial commit: Backend separado"
    }
    $existingRemote = git remote get-url origin -ErrorAction SilentlyContinue
    if (-not $existingRemote) {
        git remote add origin "https://github.com/$GitHubUser/CRQExecComMgmtBackend.git"
    } else {
        git remote set-url origin "https://github.com/$GitHubUser/CRQExecComMgmtBackend.git"
    }
    $currentBranch = git branch --show-current
    if (-not $currentBranch) {
        git checkout -b main
    } else {
        git branch -M main
    }
    Write-Host "  [OK] Backend configurado" -ForegroundColor Green
    
    # Conectar frontend
    Write-Host "  Conectando frontend..." -ForegroundColor Gray
    Set-Location $frontendRepo
    $existingRemote = git remote get-url origin -ErrorAction SilentlyContinue
    if (-not $existingRemote) {
        git remote add origin "https://github.com/$GitHubUser/CRQExecComMgmtFrontend.git"
    } else {
        git remote set-url origin "https://github.com/$GitHubUser/CRQExecComMgmtFrontend.git"
    }
    $currentBranch = git branch --show-current
    if (-not $currentBranch) {
        git checkout -b main
    } else {
        git branch -M main
    }
    Write-Host "  [OK] Frontend configurado" -ForegroundColor Green
    
    Write-Host "`n  Agora faca push manualmente:" -ForegroundColor Cyan
    Write-Host "  cd `"$backendRepo`"" -ForegroundColor Gray
    Write-Host "  git push -u origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  cd `"$frontendRepo`"" -ForegroundColor Gray
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}

# Resumo final
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "  CONCLUIDO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repositorios:" -ForegroundColor White
Write-Host "  Backend:  https://github.com/$GitHubUser/CRQExecComMgmtBackend" -ForegroundColor Cyan
Write-Host "  Frontend: https://github.com/$GitHubUser/CRQExecComMgmtFrontend" -ForegroundColor Cyan
Write-Host ""
