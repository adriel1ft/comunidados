# Script para setup do backend (Windows PowerShell)

Write-Host "🚀 Configurando backend..." -ForegroundColor Green

# Instalar dependências
Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao instalar dependências" -ForegroundColor Red
    exit 1
}

# Build TypeScript
Write-Host "🔨 Compilando TypeScript..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao compilar TypeScript" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend configurado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "Para rodar em desenvolvimento:" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Para rodar em produção:" -ForegroundColor Cyan
Write-Host "  npm start" -ForegroundColor White
