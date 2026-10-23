# Скрипт автоматического восстановления системы после перезагрузки
# Путь: H:\ACTOR_DEV_ENV\post_reboot_init.ps1

Write-Host "Запуск скрипта восстановления..."

# 1. Исправление Docker
Write-Host "Проверка службы Docker..."
$dockerService = Get-Service docker -ErrorAction SilentlyContinue
if ($dockerService) {
    Write-Host "Перезапуск службы Docker..."
    Start-Sleep -Seconds 30 # Ожидание старта системы
    Restart-Service docker -Force
} else {
    Write-Host "Служба Docker не найдена, пропуск."
}

# 2. Аудит
$event = "System rebooted. Gemini CLI auto-audit activated."
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Пишем в текстовый лог
Add-Content -Path "H:\ACTOR_DEV_ENV\audit_events.log" -Value "$timestamp`:$event"

# Пишем JSON-событие
$entry = @{
    timestamp = (Get-Date -UFormat %s)
    event     = "system_reboot"
    message   = $event
}
$entry | ConvertTo-Json -Depth 3 | Add-Content -Path "H:\ACTOR_DEV_ENV\audit_log.json"

# 3. Отключение всплывающих окон (уведомлений)
Write-Host "Отключение уведомлений..."
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" -Name "NOC_GLOBAL_SETTING_TOASTS_ENABLED" -Value 0 -ErrorAction SilentlyContinue

# 4. Оптимизация автозагрузки
Write-Host "Восстановление завершено."
