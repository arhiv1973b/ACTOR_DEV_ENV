# ============================================================
#  A©tor Task Installer — установка в Windows Task Scheduler
#  Запуск: PowerShell от имени Администратора
#  20.04.2026
# ============================================================

$TASK_NAME   = "ACtorAutoPush"
$SCRIPT_PATH = "C:\Users\arhiv\scripts\actor_autopush.ps1"
$SCRIPTS_DIR = "C:\Users\arhiv\scripts"
$LOG_FILE    = "C:\Users\arhiv\scripts\actor_autopush.log"

# ── Создать папку для скриптов
if (-not (Test-Path $SCRIPTS_DIR)) {
    New-Item -ItemType Directory -Path $SCRIPTS_DIR -Force | Out-Null
    Write-Host "Создана папка: $SCRIPTS_DIR"
}

# ── Проверить наличие основного скрипта
if (-not (Test-Path $SCRIPT_PATH)) {
    Write-Host "ОШИБКА: Скрипт не найден: $SCRIPT_PATH" -ForegroundColor Red
    Write-Host "Скопируй actor_autopush.ps1 в $SCRIPTS_DIR и запусти снова."
    exit 1
}

# ── Удалить старую задачу если есть
if (Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Host "Старая задача удалена."
}

# ── Настройка действия
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$SCRIPT_PATH`""

# ── Триггеры:
#    1. При запуске системы (независимо от пользователя)
#    2. Каждые 6 часов (перезапуск если скрипт завершился)
$triggerBoot    = New-ScheduledTaskTrigger -AtStartup
$triggerRepeat  = New-ScheduledTaskTrigger -Daily -At "00:05"

# Добавить повторение каждые 6ч к ежедневному триггеру
$triggerRepeat.RepetitionInterval = "PT6H"
$triggerRepeat.RepetitionDuration = "P1D"

# ── Настройки задачи
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Days 365) `
    -RestartCount 99 `
    -RestartInterval (New-TimeSpan -Minutes 5) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false

# ── Принципал: SYSTEM — не требует логина пользователя
$principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# ── Регистрация задачи
$task = Register-ScheduledTask `
    -TaskName $TASK_NAME `
    -Action $action `
    -Trigger @($triggerBoot, $triggerRepeat) `
    -Settings $settings `
    -Principal $principal `
    -Description "A©tor AutoPush: Drive sync + days counter + GitHub Pages | CASE-MACHERET-1997-2026"

if ($task) {
    Write-Host ""
    Write-Host "=== ЗАДАЧА УСТАНОВЛЕНА ===" -ForegroundColor Green
    Write-Host "Имя:        $TASK_NAME"
    Write-Host "Скрипт:     $SCRIPT_PATH"
    Write-Host "Запуск:     при старте системы + каждые 6ч"
    Write-Host "Сессия:     не требуется (SYSTEM)"
    Write-Host "Онлайн:     не требуется"
    Write-Host "Лог:        $LOG_FILE"
    Write-Host ""
    Write-Host "Для немедленного запуска:"
    Write-Host "  Start-ScheduledTask -TaskName '$TASK_NAME'"
} else {
    Write-Host "ОШИБКА при регистрации задачи." -ForegroundColor Red
}

# ── Немедленный первый запуск
$answer = Read-Host "Запустить задачу прямо сейчас? (y/n)"
if ($answer -eq 'y') {
    Start-ScheduledTask -TaskName $TASK_NAME
    Start-Sleep -Seconds 2
    $state = (Get-ScheduledTask -TaskName $TASK_NAME).State
    Write-Host "Состояние задачи: $state" -ForegroundColor Cyan
    Write-Host "Лог: $LOG_FILE"
}
