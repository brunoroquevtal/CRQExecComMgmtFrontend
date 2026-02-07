# Script para testar se a variável SSL está sendo lida corretamente

Write-Host "=== TESTE DE VARIAVEL SSL ===" -ForegroundColor Cyan
Write-Host ""

# Definir variável
$env:DISABLE_SSL_VERIFY = 'true'

Write-Host "Variavel definida:" -ForegroundColor Yellow
Write-Host "  DISABLE_SSL_VERIFY = $env:DISABLE_SSL_VERIFY" -ForegroundColor White
Write-Host ""

# Testar se Python consegue ler
Write-Host "Testando leitura via Python..." -ForegroundColor Yellow
python -c "import os; print(f'DISABLE_SSL_VERIFY = {os.getenv(\"DISABLE_SSL_VERIFY\", \"NAO_ENCONTRADO\")}')"

Write-Host ""
Write-Host "Se mostrar 'true', a variavel esta sendo lida corretamente." -ForegroundColor Green
Write-Host "Se mostrar 'NAO_ENCONTRADO', ha um problema com a variavel." -ForegroundColor Red
Write-Host ""

# Executar o script com a variável
Write-Host "Executando sync_excel.py com a variavel definida..." -ForegroundColor Yellow
Write-Host ""

python sync_excel.py --help
