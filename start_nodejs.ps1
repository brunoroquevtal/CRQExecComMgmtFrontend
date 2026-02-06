# Script PowerShell para iniciar backend e frontend simultaneamente

Write-Host "🚀 Iniciando aplicação Node.js/React..." -ForegroundColor Cyan

# Verificar se Node.js está instalado
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js não está instalado. Por favor, instale Node.js primeiro." -ForegroundColor Red
    exit 1
}

# Iniciar backend
Write-Host "`n📦 Iniciando backend..." -ForegroundColor Yellow
Set-Location backend
if (-not (Test-Path "node_modules")) {
    Write-Host "  Instalando dependências do backend..." -ForegroundColor Gray
    npm install
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Minimized
Set-Location ..

# Aguardar backend iniciar
Start-Sleep -Seconds 3

# Iniciar frontend
Write-Host "⚛️  Iniciando frontend..." -ForegroundColor Yellow
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "  Instalando dependências do frontend..." -ForegroundColor Gray
    npm install
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Minimized
Set-Location ..

Write-Host "`n✅ Aplicação iniciada!" -ForegroundColor Green
Write-Host "   Backend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "`n💡 Duas janelas PowerShell foram abertas (backend e frontend)" -ForegroundColor Yellow
Write-Host "   Feche-as para encerrar os serviços" -ForegroundColor Yellow
