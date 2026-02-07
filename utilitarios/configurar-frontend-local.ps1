# Script para configurar o frontend local para usar o backend no Netlify
# Execute este script na raiz do projeto

Write-Host "🔧 Configurando Frontend Local" -ForegroundColor Cyan
Write-Host ""

$envFile = "frontend\.env.local"
$envExample = "frontend\.env.example"

# Verificar se o arquivo já existe
if (Test-Path $envFile) {
    Write-Host "⚠️  O arquivo .env.local já existe!" -ForegroundColor Yellow
    $overwrite = Read-Host "Deseja sobrescrever? (s/N)"
    if ($overwrite -ne "s" -and $overwrite -ne "S") {
        Write-Host "❌ Operação cancelada." -ForegroundColor Red
        exit
    }
}

Write-Host "📝 Criando arquivo .env.local..." -ForegroundColor Green

# Perguntar qual opção o usuário quer
Write-Host ""
Write-Host "Escolha a opção de backend:" -ForegroundColor Cyan
Write-Host "1. Backend no Netlify (produção) - https://crqcommunidationbackend.netlify.app/api"
Write-Host "2. Backend no Netlify usando Functions - https://crqcommunidationbackend.netlify.app/.netlify/functions/api"
Write-Host "3. Backend local (localhost:3000) - http://localhost:3000/api"
Write-Host "4. Usar proxy do Vite (padrão) - não criar arquivo"
Write-Host ""

$option = Read-Host "Digite o número da opção (1-4)"

$content = @"
# Configuração para desenvolvimento local
# Gerado automaticamente em $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

switch ($option) {
    "1" {
        $content += "`nVITE_API_URL=https://crqcommunidationbackend.netlify.app/api"
        Write-Host "✅ Configurado para usar backend no Netlify (produção)" -ForegroundColor Green
    }
    "2" {
        $content += "`nVITE_API_URL=https://crqcommunidationbackend.netlify.app/.netlify/functions/api"
        Write-Host "✅ Configurado para usar backend no Netlify (Functions)" -ForegroundColor Green
    }
    "3" {
        $content += "`nVITE_API_URL=http://localhost:3000/api"
        Write-Host "✅ Configurado para usar backend local" -ForegroundColor Green
    }
    "4" {
        Write-Host "ℹ️  Nenhum arquivo criado. O frontend usará o proxy do Vite (localhost:3000)" -ForegroundColor Yellow
        exit
    }
    default {
        Write-Host "❌ Opção inválida!" -ForegroundColor Red
        exit
    }
}

# Criar o arquivo
$content | Out-File -FilePath $envFile -Encoding UTF8

Write-Host ""
Write-Host "✅ Arquivo .env.local criado com sucesso!" -ForegroundColor Green
Write-Host "📍 Localização: $envFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Execute: cd frontend"
Write-Host "   2. Execute: npm run dev"
Write-Host "   3. Acesse: http://localhost:5173"
Write-Host ""
