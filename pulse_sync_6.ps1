# Pulse Synchronization Script (Terminal 6)
# Coordinates Docker, WSL, Git, and Gemini CLI

Write-Host "--- [PULSE-SYNC-6] Инициализация системного цикла ---" -ForegroundColor Cyan

# 1. Проверка Docker/WSL
Write-Host "[1/4] Проверка Docker Daemon..." -ForegroundColor Yellow
$docker_info = docker info 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Docker активен." -ForegroundColor Green
} else {
    Write-Host "CRITICAL: Docker не отвечает. Выполните: wsl --shutdown" -ForegroundColor Red
}

# 2. Проверка Git
Write-Host "[2/4] Синхронизация весов (Git)..." -ForegroundColor Yellow
git fetch origin
$status = git status --porcelain
if ($status -eq "") {
    Write-Host "OK: Репозиторий синхронизирован." -ForegroundColor Green
} else {
    Write-Host "WARN: Есть локальные изменения. Требуется коммит." -ForegroundColor Yellow
}

# 3. Проверка Ollama
Write-Host "[3/4] Проверка нейронного ядра (Ollama)..." -ForegroundColor Yellow
$ollama_check = docker exec actor_ollama curl -s http://localhost:11434 2>$null
if ($ollama_check -eq "Ollama is running") {
    Write-Host "OK: Ядро Ollama в сети." -ForegroundColor Green
} else {
    Write-Host "WARN: Ollama не отвечает. Попытка перезапуска..." -ForegroundColor Yellow
    docker restart actor_ollama
}

# 4. Gemini CLI
Write-Host "[4/4] Gemini CLI статус..." -ForegroundColor Yellow
gemini --version

Write-Host "--- [PULSE-SYNC-6] Цикл обратной связи активен ---" -ForegroundColor Cyan
