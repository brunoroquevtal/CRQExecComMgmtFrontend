# Script para gerar executável onefile do sincronizador
# Requer: Python 3.x e PyInstaller instalado

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GERADOR DE EXECUTAVEL - SINCRONIZADOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está instalado
Write-Host "Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERRO] Python nao encontrado!" -ForegroundColor Red
    Write-Host "Instale Python 3.x de: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Verificar se PyInstaller está instalado
Write-Host ""
Write-Host "Verificando PyInstaller..." -ForegroundColor Yellow
try {
    $pyinstallerVersion = pyinstaller --version 2>&1
    Write-Host "[OK] PyInstaller encontrado: $pyinstallerVersion" -ForegroundColor Green
} catch {
    Write-Host "[AVISO] PyInstaller nao encontrado. Instalando..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao instalar PyInstaller!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] PyInstaller instalado!" -ForegroundColor Green
}

# Verificar se as dependências estão instaladas
Write-Host ""
Write-Host "Verificando dependencias..." -ForegroundColor Yellow
if (Test-Path "requirements_sync.txt") {
    Write-Host "[OK] Arquivo requirements_sync.txt encontrado" -ForegroundColor Green
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    python -m pip install -r requirements_sync.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao instalar dependencias!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Dependencias instaladas!" -ForegroundColor Green
} else {
    Write-Host "[AVISO] requirements_sync.txt nao encontrado. Instalando dependencias basicas..." -ForegroundColor Yellow
    python -m pip install pandas openpyxl requests pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] Falha ao instalar dependencias!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Dependencias instaladas!" -ForegroundColor Green
}

# Limpar builds anteriores
Write-Host ""
Write-Host "Limpando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "[OK] Pasta build removida" -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "[OK] Pasta dist removida" -ForegroundColor Green
}
if (Test-Path "sync_excel.spec") {
    Remove-Item -Force "sync_excel.spec"
    Write-Host "[OK] Arquivo .spec removido" -ForegroundColor Green
}

# Gerar executável
Write-Host ""
Write-Host "Gerando executavel onefile..." -ForegroundColor Yellow
Write-Host "Isso pode levar alguns minutos..." -ForegroundColor Gray

$scriptPath = Join-Path $PSScriptRoot "sync_excel.py"

python -m PyInstaller `
    --onefile `
    --name "sync_excel" `
    --console `
    --clean `
    --noconfirm `
    --hidden-import pandas `
    --hidden-import openpyxl `
    --hidden-import requests `
    $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "EXECUTAVEL GERADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    $exePath = Join-Path $PSScriptRoot "dist\sync_excel.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "Arquivo: $exePath" -ForegroundColor Cyan
        Write-Host "Tamanho: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Para usar o executavel:" -ForegroundColor Yellow
        Write-Host "  .\dist\sync_excel.exe" -ForegroundColor White
        Write-Host "  .\dist\sync_excel.exe --mode bulk" -ForegroundColor White
        Write-Host "  .\dist\sync_excel.exe `"C:\caminho\arquivo.xlsx`"" -ForegroundColor White
    } else {
        Write-Host "[AVISO] Executavel nao encontrado em dist\" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[ERRO] Falha ao gerar executavel!" -ForegroundColor Red
    Write-Host "Verifique os erros acima." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
