# Script para testar a API no Netlify e diagnosticar problemas

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DE API NO NETLIFY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://crqcommunidationbackend.netlify.app"

# Teste 1: Health Check
Write-Host "1. Testando Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    Write-Host "   [OK] Health check funcionando!" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    Write-Host "   Database: $($health.database)" -ForegroundColor Gray
} catch {
    Write-Host "   [ERRO] Health check falhou!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Teste 2: Root endpoint
Write-Host "2. Testando Root endpoint..." -ForegroundColor Yellow
try {
    $root = Invoke-RestMethod -Uri "$baseUrl/" -Method Get -ErrorAction Stop
    Write-Host "   [OK] Root endpoint funcionando!" -ForegroundColor Green
    Write-Host "   Message: $($root.message)" -ForegroundColor Gray
} catch {
    Write-Host "   [ERRO] Root endpoint falhou!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Teste 3: GET /api/activities
Write-Host "3. Testando GET /api/activities..." -ForegroundColor Yellow
try {
    $activities = Invoke-RestMethod -Uri "$baseUrl/api/activities" -Method Get -ErrorAction Stop
    Write-Host "   [OK] GET /api/activities funcionando!" -ForegroundColor Green
    Write-Host "   Total de atividades: $($activities.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   [ERRO] GET /api/activities falhou!" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Resposta: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""

# Teste 4: PUT /api/activity (teste simples)
Write-Host "4. Testando PUT /api/activity..." -ForegroundColor Yellow
$testActivity = @{
    seq = 999
    sequencia = "REDE"
    atividade = "Teste de sincronizacao"
    inicio = "01/01/2024 10:00:00"
    fim = "01/01/2024 11:00:00"
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
        "Accept" = "application/json"
    }
    
    $response = Invoke-RestMethod `
        -Uri "$baseUrl/api/activity" `
        -Method Put `
        -Body $testActivity `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "   [OK] PUT /api/activity funcionando!" -ForegroundColor Green
    Write-Host "   Resposta: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "   [ERRO] PUT /api/activity falhou!" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   Resposta do servidor:" -ForegroundColor Yellow
            Write-Host "   $responseBody" -ForegroundColor Red
            
            # Tentar parsear JSON
            try {
                $errorJson = $responseBody | ConvertFrom-Json
                if ($errorJson.error) {
                    Write-Host ""
                    Write-Host "   Erro detalhado: $($errorJson.error)" -ForegroundColor Red
                }
            } catch {
                # Não é JSON, mostrar como está
            }
        } catch {
            Write-Host "   Não foi possível ler a resposta do servidor" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE CONCLUIDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se PUT /api/activity falhou:" -ForegroundColor Yellow
Write-Host "  1. Verifique os logs do Netlify Functions" -ForegroundColor White
Write-Host "  2. Verifique as variaveis de ambiente no Netlify" -ForegroundColor White
Write-Host "  3. Verifique se o banco de dados esta configurado" -ForegroundColor White
Write-Host "  4. Veja o arquivo SOLUCAO_HTTP_500_NETLIFY.md" -ForegroundColor White
