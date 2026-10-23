# Orchestrator Handshake Protocol (Terminal 6)
# Poétape connection establishment and feedback loop initialization

Write-Host "--- [HANDSHAKE PROTOCOL] Инициализация рукопожатий ---" -ForegroundColor Magenta

# 1. WSL Handshake
Write-Host "[1/5] Проверка уровня виртуализации (WSL)..." -ForegroundColor Yellow
$wsl_status = wsl --status 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "HANDSHAKE: WSL активен." -ForegroundColor Green
} else {
    Write-Host "HANDSHAKE: Ошибка WSL. Перезапуск..." -ForegroundColor Red
    wsl --shutdown
}

# 2. Docker Handshake
Write-Host "[2/5] Установление связи с Docker Daemon..." -ForegroundColor Yellow
$docker_status = docker info 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "HANDSHAKE: Docker Daemon доступен." -ForegroundColor Green
} else {
    Write-Host "HANDSHAKE: Docker не отвечает. Запуск Docker Desktop..." -ForegroundColor Red
    # Упрощенный запуск - адаптация под вашу систему
    & "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 30
}

# 3. Ollama Handshake
Write-Host "[3/5] Подключение нейронного узла (Ollama)..." -ForegroundColor Yellow
$ollama_ready = $false
for($i=0; $i -lt 5; $i++) {
    $res = docker exec actor_ollama curl -s http://localhost:11434 2>$null
    if ($res -eq "Ollama is running") {
        Write-Host "HANDSHAKE: Ollama подключена." -ForegroundColor Green
        $ollama_ready = $true
        break
    } else {
        Write-Host "HANDSHAKE: Ожидание Ollama... ($($i+1)/5)" -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}
if (-not $ollama_ready) { Write-Host "HANDSHAKE: ОШИБКА подключения Ollama!" -ForegroundColor Red }

# 4. Git Weight/Connection Handshake
Write-Host "[4/5] Синхронизация весов (Git Handshake)..." -ForegroundColor Yellow
git remote update
$git_check = git status -uno
if ($LASTEXITCODE -eq 0) {
    Write-Host "HANDSHAKE: Git-связь установлена." -ForegroundColor Green
} else {
    Write-Host "HANDSHAKE: Ошибка Git-связи." -ForegroundColor Red
}

# 5. Gemini CLI Handshake
Write-Host "[5/5] Проверка Gemini-интерфейса..." -ForegroundColor Yellow
$gemini_check = gemini --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "HANDSHAKE: Gemini CLI готов к потоку." -ForegroundColor Green
} else {
    Write-Host "HANDSHAKE: Ошибка Gemini CLI." -ForegroundColor Red
}

Write-Host "--- [HANDSHAKE PROTOCOL] Система синхронизирована. ПУЛЬС-6 АКТИВЕН. ---" -ForegroundColor Magenta
Write-Host "Используйте .\pulse_sync_6.ps1 для поддержания потока." -ForegroundColor Cyan
