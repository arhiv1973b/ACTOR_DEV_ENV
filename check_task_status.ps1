# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

# 1. Получение основных сведений о последнем запуске задачи
$TaskName = "A©tor_Event1001_Alert"

Write-Host "=== ОБЩИЙ СТАТУС ЗАДАЧИ: $TaskName ===" -ForegroundColor Cyan
$TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue

if ($TaskInfo) {
    [PSCustomObject]@{
        "Имя задачи"            = $TaskName
        "Время последнего запуска" = $TaskInfo.LastRunTime
        "Код результата (HEX)"     = ("0x{0:X8}" -f $TaskInfo.LastTaskResult) + $(if ($TaskInfo.LastTaskResult -eq 0) {" (Успех)"} else {" (Ошибка)"})
        "Следующий запуск"      = $TaskInfo.NextRunTime
        "Пропущенных запусков"   = $TaskInfo.NumberOfMissedRuns
    } | Format-List
} else {
    Write-Host "Задача $TaskName не найдена в Планировщике." -ForegroundColor Red
}

# 2. Извлечение детальных записей из операционного журнала Планировщика задач
Write-Host "=== ИСТОРИЯ СОБЫТИЙ ИЗ МИКРО-ЖУРНАЛА ТАСКЕРА ===" -ForegroundColor Cyan
try {
    Get-WinEvent -FilterHashtable @{
        LogName = 'Microsoft-Windows-TaskScheduler/Operational'
    } -ErrorAction Stop |
    Where-Object { $_.Message -like "*$TaskName*" } |
    Select-Object -First 10 |
    Select-Object TimeCreated, Id, @{
        N = 'Детали события'
        E = {
            switch ($_.Id) {
                100 { "Запуск процесса задачи" }
                102 { "Успешное завершение задачи" }
                103 { "Сбой выполнения задачи" }
                200 { "Инициация действия (Exec)" }
                201 { "Действие завершено" }
                default { $_.Message.Split("`n")[0] }
            }
        }
    } | Format-Table -AutoSize
} catch {
    Write-Host "Операционный журнал Планировщика недоступен или отключен." -ForegroundColor Yellow
}
