# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, Jus Cogens, ВДПЧ 1948, TI-ULA
# Description: Health Check & Log Diagnostics for Actor_CloudLink_Audit

$TaskName = "Actor_CloudLink_Audit"
$WorkspacePath = "H:\ACTOR_DEV_ENV"
$LogDirectory = "$WorkspacePath\secure_logs"

$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -eq $Task) {
    Write-Host "[ОШИБКА] Задача '$TaskName' не найдена в Планировщике Windows." -ForegroundColor Red
    exit
}

$TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
$LastResult = $TaskInfo.LastTaskResult

Write-Host "`n=======================================================" -ForegroundColor Cyan
Write-Host "            СТАТУС ПАЙПЛАЙНА TI-ULA" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Имя задачи:      $($Task.TaskName)"
Write-Host "Текущее сост.:   $($Task.State)"
Write-Host "Последний старт: $($TaskInfo.LastRunTime)"
Write-Host "Следующий старт: $($TaskInfo.NextRunTime)"
Write-Host "Код возврата:    $LastResult" -ForegroundColor ($LastResult -eq 0 ? "Green" : "Yellow")
Write-Host "=======================================================`n" -ForegroundColor Cyan

if ($LastResult -ne 0 -and $LastResult -ne 267009) {
    Write-Host "[ДИАГНОСТИКА] Последние строки лога:" -ForegroundColor Yellow
    $LatestLog = Get-ChildItem -Path $LogDirectory -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($LatestLog) {
        Get-Content $LatestLog.FullName -Tail 5 -Encoding utf8 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
    }
}
