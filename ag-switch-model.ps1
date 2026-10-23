$configPath = "$env:APPDATA\aichat\config.yaml"
$priorityModels = @("gemini:gemini-2.5-pro", "gemini:gemini-2.0-flash", "gemini:gemini-2.0-flash-lite")

$test = aichat -m $priorityModels[0] -- "ping" 2>&1

if ($test -match "UNAVAILABLE" -or $test -match "quota" -or $test -match "Error") {
    Write-Host "Сбой: $($priorityModels[0]). Переключение на резерв..." -ForegroundColor Yellow
    
    # Сдвиг приоритета: переписываем файл с моделью из индекса 1
    (Get-Content $configPath) -replace "model: .*", "model: $($priorityModels[1])" | Set-Content $configPath
    
    Write-Host "Узел переключен на $($priorityModels[1])" -ForegroundColor Green
} else {
    Write-Host "Узел $($priorityModels[0]) подтвержден как активный." -ForegroundColor Cyan
}