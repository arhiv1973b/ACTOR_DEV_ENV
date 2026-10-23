# ⚖ Автоматическая синхронизация бэкапов и крипто-манифестов через rclone
$BackupSource = "..\ACTOR_SECURE_BACKUPS"
$ManifestsSource = "05_CRYPTO_MANIFESTS"
$TargetDir = "F:\Мой диск\ACTOR_DEV_ENV_SECURE_VAULT"

Write-Host "⚖ Проверка доступности диска Google Drive (F:\)..." -ForegroundColor Cyan

if (!(Test-Path -Path "F:\Мой диск")) {
    Write-Error "Критическая ошибка: Диск F:\Мой диск не смонтирован или недоступен."
    exit 1
}

# Создание целевой директории в облаке, если она отсутствует
if (!(Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

# 1. Копирование актуальных бэкапов
if (Test-Path -Path $BackupSource) {
    Write-Host "Синхронизация архивов бэкапов..." -ForegroundColor Yellow
    rclone copy "$BackupSource" "$TargetDir\BACKUPS" --progress --transfers 4
} else {
    Write-Warning "Директория бэкапов $BackupSource не найдена."
}

# 2. Копирование папки крипто-манифестов
if (Test-Path -Path $ManifestsSource) {
    Write-Host "Синхронизация папки 05_CRYPTO_MANIFESTS..." -ForegroundColor Yellow
    rclone copy "$ManifestsSource" "$TargetDir\05_CRYPTO_MANIFESTS" --progress --transfers 4
} else {
    Write-Warning "Директория $ManifestsSource не найдена."
}

Write-Host "`nСинхронизация с облачным депонитом успешно завершена." -ForegroundColor Green
