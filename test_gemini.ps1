Write-Host "=== Проверка rg.exe ==="
$rgPath = "H:\ACTOR_DEV_ENV\.venv\Scripts\rg.exe"
if (Test-Path $rgPath) {
    Write-Host "Ripgrep найден в .venv\Scripts:" $rgPath
} else {
    Write-Host "Ripgrep не найден в .venv\Scripts. Ищу настоящий rg.exe..."
    $realRg = (Get-ChildItem -Path "C:\Users\arhiv\AppData\Local\Microsoft\WinGet\Packages\" -Filter "rg.exe" -Recurse -ErrorAction SilentlyContinue).FullName | Select-Object -First 1
    if ($realRg) {
        Write-Host "Найден настоящий rg.exe:" $realRg
        try {
            New-Item -ItemType SymbolicLink -Path $rgPath -Target $realRg -Force | Out-Null
            Write-Host "Симлинк создан: $rgPath -> $realRg"
        } catch {
            Write-Host "Ошибка создания симлинка: $_"
        }
    } else {
        Write-Host "Не удалось найти rg.exe через Winget."
    }
}

Write-Host "`n=== Текущий PATH процесса ==="
[System.Environment]::GetEnvironmentVariable("Path","Process") -split ";" | ForEach-Object { Write-Host $_ }

Write-Host "`n=== Проверка MCP ==="
if (Get-Command mcp -ErrorAction SilentlyContinue) {
    Write-Host "MCP найден:" (Get-Command mcp).Source
    Write-Host "Список доступных команд MCP:"
    try {
        mcp --help
        Write-Host "`n=== Выполнение mcp list ==="
        mcp list
    } catch {
        Write-Host "Ошибка выполнения MCP: $_"
    }
} else {
    Write-Host "MCP не найден!"
}

Write-Host "`n=== Тест Gemini CLI ==="
try {
    gemini --prompt "test"
} catch {
    Write-Host "Ошибка запуска Gemini: $_"
}
