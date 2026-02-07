# Script para criar branch, commit, PR e merge automaticamente
# Uso: .\fazer-pr-automatico.ps1 "Descricao do commit"

param(
    [Parameter(Mandatory=$true)]
    [string]$CommitMessage
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Green "========================================"
Write-ColorOutput Green "CRIAR BRANCH, PR E MERGE AUTOMATICO"
Write-ColorOutput Green "========================================"
Write-Host ""

# 1. Verificar se há mudanças
Write-ColorOutput Yellow "1. Verificando mudancas..."
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-ColorOutput Red "Nenhuma mudanca para commitar!"
    exit 0
}

Write-ColorOutput Green "Mudancas encontradas:"
Write-Host $status
Write-Host ""

# 2. Criar nome da branch baseado na mensagem
$branchName = $CommitMessage -replace '[^a-zA-Z0-9]', '-' -replace '-+', '-' -replace '^-|-$', '' -replace '^(.{0,50}).*$', '$1'
$branchName = "feature/$branchName-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$branchName = $branchName.ToLower()

Write-ColorOutput Yellow "2. Criando branch: $branchName"
git checkout -b $branchName
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput Red "Erro ao criar branch!"
    exit 1
}
Write-ColorOutput Green "Branch criada com sucesso!"
Write-Host ""

# 3. Adicionar todas as mudanças
Write-ColorOutput Yellow "3. Adicionando mudancas..."
git add -A
Write-ColorOutput Green "Mudancas adicionadas!"
Write-Host ""

# 4. Fazer commit
Write-ColorOutput Yellow "4. Fazendo commit..."
git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput Red "Erro ao fazer commit!"
    exit 1
}
Write-ColorOutput Green "Commit realizado!"
Write-Host ""

# 5. Fazer push da branch
Write-ColorOutput Yellow "5. Fazendo push da branch..."
git push -u origin $branchName
if ($LASTEXITCODE -ne 0) {
    Write-ColorOutput Red "Erro ao fazer push!"
    exit 1
}
Write-ColorOutput Green "Push realizado!"
Write-Host ""

# 6. Criar Pull Request
Write-ColorOutput Yellow "6. Criando Pull Request..."

# Verificar se GitHub CLI está disponível
$ghAvailable = $false
try {
    $ghVersion = gh --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ghAvailable = $true
    }
} catch {
    $ghAvailable = $false
}

if ($ghAvailable) {
    Write-ColorOutput Cyan "GitHub CLI encontrado! Criando PR..."
    $prTitle = $CommitMessage
    $prBody = "Pull request criado automaticamente`n`nCommit: $CommitMessage"
    
    $prOutput = gh pr create --title $prTitle --body $prBody --base main --head $branchName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput Green "Pull Request criado com sucesso!"
        Write-Host $prOutput
        
        # Extrair número do PR
        $prNumber = $prOutput | Select-String -Pattern 'pull/(\d+)' | ForEach-Object { $_.Matches[0].Groups[1].Value }
        
        if ($prNumber) {
            Write-ColorOutput Yellow "7. Fazendo merge do Pull Request #$prNumber..."
            gh pr merge $prNumber --merge --delete-branch
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput Green "Pull Request mesclado com sucesso!"
                Write-Host ""
                Write-ColorOutput Green "========================================"
                Write-ColorOutput Green "PROCESSO CONCLUIDO!"
                Write-ColorOutput Green "========================================"
                Write-Host ""
                Write-ColorOutput Cyan "Branch: $branchName"
                Write-ColorOutput Cyan "PR: #$prNumber"
                Write-ColorOutput Cyan "Status: Merged"
            } else {
                Write-ColorOutput Red "Erro ao fazer merge do PR!"
                Write-ColorOutput Yellow "PR criado, mas merge falhou. Faca manualmente:"
                Write-Host "gh pr merge $prNumber --merge --delete-branch"
            }
        } else {
            Write-ColorOutput Yellow "Nao foi possivel extrair o numero do PR. Faca merge manualmente."
        }
    } else {
        Write-ColorOutput Red "Erro ao criar Pull Request!"
        Write-Host $prOutput
        Write-ColorOutput Yellow "Crie o PR manualmente no GitHub ou instale GitHub CLI:"
        Write-Host "winget install --id GitHub.cli"
    }
} else {
    Write-ColorOutput Yellow "GitHub CLI nao encontrado. Instale para automatizar PRs:"
    Write-Host "winget install --id GitHub.cli"
    Write-Host ""
    Write-ColorOutput Cyan "Ou crie o PR manualmente no GitHub:"
    Write-Host "https://github.com/brunoroquevtal/CRQExecComMgmtFrontend/compare/main...$branchName"
    Write-Host ""
    Write-ColorOutput Yellow "Depois, faca merge manualmente no GitHub ou execute:"
    Write-Host "gh pr merge <numero-do-pr> --merge --delete-branch"
}

Write-Host ""
