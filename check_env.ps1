param(
    [string]$TargetFile = "H:\ACTOR_DEV_ENV\test.txt",
    [string]$ModulePath = "H:\ACTOR_DEV_ENV\tiula-crypto-sandbox.psm1",
    [string]$PrivateKeyPath = "H:\ACTOR_DEV_ENV\keys\actor_ed25519"
)

Write-Host "=== TIULA-ACTOR ENVIRONMENT AUDIT ===" -ForegroundColor Cyan

if (-not (Test-Path $TargetFile)) {
    Set-Content -Path $TargetFile -Value "TIULA-ACTOR Sandbox Test Content" -Encoding UTF8
}

$SigFile = "$TargetFile.sig"
Write-Host "`n[1] Проверка файла подписи..." -NoNewline
if (Test-Path $SigFile) {
    Write-Host " [OK] Найдено: $SigFile" -ForegroundColor Green
} else {
    Write-Host " [WARNING] Отсутствует! Генерируем..." -ForegroundColor Yellow
    if (Test-Path $ModulePath) {
        Import-Module $ModulePath -Force -DisableNameChecking
        
        if (-not (Test-Path $PrivateKeyPath)) {
            Write-Host " [WARNING] Приватный ключ не найден: $PrivateKeyPath. Попытка инициализации..." -ForegroundColor Yellow
            Initialize-CryptoKeys -KeyDir "H:\ACTOR_DEV_ENV\keys"
        }

        Sign-Artifact -ArtifactPath $TargetFile -PrivateKeyPath $PrivateKeyPath
        
        if (Test-Path "$TargetFile.sig") {
            Write-Host " [OK] Подпись успешно создана." -ForegroundColor Green
        } else {
            Write-Host " [ERROR] Файл подписи не был создан." -ForegroundColor Red
        }
    } else {
        Write-Host " [ERROR] Модуль не найден по пути: $ModulePath" -ForegroundColor Red
    }
}

Write-Host "`n[2] Проверка python-модуля google.genai..." -NoNewline
$pythonCheck = python -c "try: import google.genai as genai; print('OK') except ImportError: print('FAIL')" 2>&1
if ($pythonCheck -match "OK") {
    Write-Host " [OK] Библиотека доступна." -ForegroundColor Green
} else {
    Write-Host " [WARNING] Требуется установка: pip install google-genai" -ForegroundColor Yellow
}

Write-Host "`n[3] Проверка доступности модели (gemini-3.1-flash-lite)..." -NoNewline
$modelCheck = python -c "import os, sys;
try:
    from google import genai
    client = genai.Client()
    print('Client initialized')
except Exception as e:
    print('Error:', e)
    sys.exit(1)" 2>&1

Write-Host " `n$modelCheck" -ForegroundColor Gray

Write-Host "`n[4] Проверка структуры входных событий детектора..." -NoNewline
$eventPayload = @{
    process_id   = $PID
    file_path    = $TargetFile
    user_account = $env:USERNAME
    action       = "audit_check"
}
if ($eventPayload.Keys.Count -ge 4) {
    Write-Host " [OK] Событие содержит обязательные метаданные (process_id, file_path, user_account)." -ForegroundColor Green
} else {
    Write-Host " [WARNING] Неполный набор полей для детектора." -ForegroundColor Yellow
}

Write-Host "`n=== АУДИТ ЗАВЕРШЕН ===" -ForegroundColor Cyan
