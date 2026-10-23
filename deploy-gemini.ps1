# deploy-gemini.ps1 (финализированный отказоустойчивый с проверкой PDF)
$ErrorActionPreference = "Stop"
$logFile = "H:\ACTOR_DEV_ENV\deploy-gemini.log"

function Log($message, $color="White") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "$timestamp :: $message"
    Write-Host $message -ForegroundColor $color
    Add-Content -Path $logFile -Value $line
}

Log "--- Запуск развертывания Gemini CLI ---" "Cyan"

# 1. Запуск Docker Compose
try {
    Log "Запуск Docker Compose..." "Green"
    docker compose -p gemini-env up -d 2>&1 | Tee-Object -FilePath $logFile -Append
} catch {
    Log "Ошибка запуска Docker Compose: $_" "Red"
    exit 1
}

# 2. Запуск Python HTTP-сервера для F:\Мой диск
try {
    Log "Запуск HTTP-сервера для F:\Мой диск..." "Green"
    Start-Process -FilePath "python" -ArgumentList "-m http.server 8000" -WorkingDirectory "F:\Мой диск" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    try {
        Invoke-WebRequest -Uri "http://host.docker.internal:8000" -UseBasicParsing | Out-Null
        Log "HTTP-сервер доступен по адресу http://host.docker.internal:8000/" "Green"
    } catch {
        Log "HTTP-сервер не отвечает. Проверь Python или порт 8000." "Red"
    }
} catch {
    Log "Не удалось запустить HTTP-сервер. Проверь наличие Python." "Red"
}

# 3. Проверка контейнера
Start-Sleep -Seconds 5
try {
    Log "Проверка контейнера gemini-cli..." "Green"
    docker ps --filter "name=gemini-cli" 2>&1 | Tee-Object -FilePath $logFile -Append
} catch {
    Log "Контейнер gemini-cli не найден. Перезапуск Docker Desktop..." "Red"
    Stop-Process -Name "Docker Desktop" -Force
    Start-Sleep -Seconds 10
    Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Log "Docker Desktop перезапущен." "Yellow"
}

# 4. Тест-доступ к PDF и метаданные
try {
    $testFile = "Zaporojan.pdf"
    $localPath = "H:\ACTOR_DEV_ENV\$testFile"
    Log "Проверка доступа к файлу $testFile через HTTP..." "Green"
    Invoke-WebRequest -Uri "http://host.docker.internal:8000/$testFile" -OutFile $localPath
    $fileInfo = Get-Item $localPath
    Log "Файл $testFile успешно скачан." "Green"
    Log "Метаданные: Размер = $($fileInfo.Length) байт, Дата изменения = $($fileInfo.LastWriteTime)" "Yellow"
} catch {
    Log "Не удалось скачать тестовый PDF или получить метаданные. $_" "Red"
}

Log "--- Развертывание завершено ---" "Cyan"
