# Minha Jornada - Script de Inicialização
# Execute este arquivo para iniciar a aplicação

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Minha Jornada - Iniciando Aplicacao" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = "c:\Users\caxa\Documents\projto my t\backend"

Write-Host "📍 Iniciando Backend Flask..." -ForegroundColor Yellow
Write-Host "📂 Diretório: $backendPath" -ForegroundColor Gray
Write-Host ""

Set-Location $backendPath
python app.py

Write-Host ""
Write-Host "❌ Backend finalizado" -ForegroundColor Red
