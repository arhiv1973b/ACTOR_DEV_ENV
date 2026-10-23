# 1. Принудительная установка переменной окружения на Gemini 3.5 Pro для текущей сессии
$env:GEMINI_MODEL="gemini-3.5-pro"
[Environment]::SetEnvironmentVariable("GEMINI_MODEL", "gemini-3.5-pro", "User")

# 2. Поиск и замена ошибочно прописанной модели во всех файлах инфраструктуры шлюза
Write-Host "Сканирование конфигурации на наличие ошибочной Flash-модели..." -ForegroundColor Yellow

Get-ChildItem -Path "H:\ACTOR_DEV_ENV" -Include .env, *.json, *.py, .actor_socket, config.* -Recurse -ErrorAction SilentlyContinue |
Select-String -Pattern "gemini-(.*)flash(.*)" |
ForEach-Object {
    $filePath = $_.Path
    # Заменяем любые упоминания 3.1 flash или flash-lite на старшую Gemini 3.5 Pro
    (Get-Content $filePath) -replace 'gemini-[a-zA-Z0-9.-]*flash[a-zA-Z0-9.-]*', 'gemini-3.5-pro' | Set-Content $filePath
    Write-Host "[ИСПРАВЛЕНО] Модель восстановлена на 3.5 Pro в файле: $filePath" -ForegroundColor Green
}

Write-Host "Реконфигурация на Gemini 3.5 Pro завершена. Полностью перезапустите ваш AI CLI." -ForegroundColor Cyan
