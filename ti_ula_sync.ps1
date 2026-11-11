# A©TOR_KEY="# [⚖ A©tor Declaration]"
# Скрипт синхронизации AI-Hub и TI-ULA репозиториев с обходом квот
# Включает механизм блокировки для предотвращения коллизий и атомарной CAS-стабилизации

$ErrorActionPreference = "Stop"

# Имя файла-блокировки для предотвращения параллельного запуска
$lockFile = "ti_ula_sync.lock"

if (Test-Path $lockFile) {
    Write-Host "[!] Обнаружен файл блокировки $lockFile. Другой процесс синхронизации запущен!" -ForegroundColor Red
    exit
}

New-Item -Path $lockFile -ItemType File | Out-Null
Write-Host "[*] Инициализация протокола TI-ULA Sync & Weight Harmonization..." -ForegroundColor Cyan

try {
    # 1. Проверка и очистка избыточного кэша
    Write-Host "[*] Очистка временных файлов и кэша..." -ForegroundColor Yellow
    Remove-Item -Path "cache\*" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "analysis_temp\*" -Recurse -Force -ErrorAction SilentlyContinue

    # 2. Актуализация локального индекса Evidence Vault (Использует CAS-стабилизацию внутри)
    Write-Host "[*] Индексация и Атомарная CAS-стабилизация артефактов..." -ForegroundColor Yellow
    python generate_evidence_index.py --strict

    # 3. Синхронизация с локальным зеркалом Google Drive
    $gdrivePath = "F:\Мой диск\EvidenceVault"
    if (Test-Path $gdrivePath) {
        Write-Host "[*] Синхронизация с Google Drive Mirror ($gdrivePath)..." -ForegroundColor Yellow
        # Robocopy исключает файл блокировки из синхронизации
        robocopy "." "$gdrivePath" /E /XD ".git" "node_modules" "cache" /XF "*.log" "*.tmp" "$lockFile" /MT:8 /R:1 /W:1 | Out-Null
        Write-Host "[+] Зеркало Google Drive успешно обновлено." -ForegroundColor Green
    } else {
        Write-Host "[!] Предупреждение: Путь к Google Drive недоступен, пропускаем зеркалирование." -ForegroundColor Red
    }

    # 4. Git-синхронизация
    Write-Host "[*] Выполнение Git-коммита и отправки..." -ForegroundColor Yellow
    git add .
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "ti-ula: CAS-stabilized sync [$timestamp] (A©TOR_KEY)" -ErrorAction SilentlyContinue

    # Принудительная синхронизация веток
    git push origin master:main --force

    Write-Host "[+] Синхронизация TI-ULA завершена успешно." -ForegroundColor Green
}
finally {
    # Обязательное удаление блокировки
    Remove-Item -Path $lockFile -Force -ErrorAction SilentlyContinue
}
