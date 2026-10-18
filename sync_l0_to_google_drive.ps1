<#
.SYNOPSIS
    Автоматическая синхронизация L0-манифестов, логов и ключевых артефактов
    из локального репозитория H:\ACTOR_DEV_ENV в зеркало на Google Drive F:\Мой диск\ACTOR_DEV_ENV.
.DESCRIPTION
    Скрипт работает без вызова Git, полностью исключая ошибки блокировки index.lock
    на виртуальной файловой системе Google Drive.
#>

$ErrorActionPreference = "Stop"

$SrcDir = "H:\ACTOR_DEV_ENV"
$DstDir = "F:\Мой диск\ACTOR_DEV_ENV"

# Список файлов и путей для репликации относительно корня репозитория
$FilesToSync = @(
    "audit_log.json",
    "audit_log_local.json",
    "INTEGRITY_WITNESS.json",
    "evidence/INTEGRITY_WITNESS.json",
    "evidence_manifest.json",
    "crypto_manifest.json"
)

Write-Host "[*] Запуск репликации контура L0 в Google Drive..." -ForegroundColor Cyan
Write-Host "    Источник: $SrcDir"
Write-Host "    Приемник: $DstDir"
Write-Host "--------------------------------------------------"

if (-not (Test-Path $SrcDir)) {
    Write-Error "[!] Критическая ошибка: Локальный путь источника не найден: $SrcDir"
    exit 1
}

if (-not (Test-Path $DstDir)) {
    Write-Warning "[!] Путь назначения не найден. Попытка создания директории..."
    New-Item -ItemType Directory -Force -Path $DstDir | Out-Null
}

$SyncedCount = 0
$ErrorCount = 0

foreach ($RelPath in $FilesToSync) {
    $SrcPath = Join-Path $SrcDir $RelPath
    $DstPath = Join-Path $DstDir $RelPath

    if (Test-Path $SrcPath) {
        try {
            $DstParent = Split-Path $DstPath -Parent
            if (-not (Test-Path $DstParent)) {
                New-Item -ItemType Directory -Force -Path $DstParent | Out-Null
            }
            
            Copy-Item -Path $SrcPath -Destination $DstPath -Force
            Write-Host "[+] Успешно скопировано: $RelPath" -ForegroundColor Green
            $SyncedCount++
        }
        catch {
            Write-Host "[!] Ошибка при копировании $RelPath : $_" -ForegroundColor Red
            $ErrorCount++
        }
    } else {
        Write-Host "[-] Пропущено (нет в источнике): $RelPath" -ForegroundColor Yellow
    }
}

Write-Host "--------------------------------------------------"
Write-Host "[*] Репликация завершена. Успешно: $SyncedCount, Ошибок: $ErrorCount" -ForegroundColor Cyan
