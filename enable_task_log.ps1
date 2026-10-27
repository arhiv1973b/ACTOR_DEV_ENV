# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$LogName = "Microsoft-Windows-TaskScheduler/Operational"

$LogStatus = Get-WinEvent -ListLog $LogName -ErrorAction SilentlyContinue

if ($LogStatus) {
    if (-not $LogStatus.IsEnabled) {
        Write-Host "Журнал '$LogName' отключен. Активация..." -ForegroundColor Yellow
        try {
            wevtutil.exe set-log $LogName /e:true
            $CheckStatus = Get-WinEvent -ListLog $LogName -ErrorAction SilentlyContinue
            if ($CheckStatus.IsEnabled) {
                Write-Host "Операционный журнал Планировщика задач успешно ВКЛЮЧЕН!" -ForegroundColor Green
            } else {
                Write-Host "ОШИБКА: Не удалось включить журнал. Требуются права Администратора." -ForegroundColor Red
            }
        } catch {
            Write-Host "ИСКЛЮЧЕНИЕ: Для изменения настроек журнала требуются права Администратора." -ForegroundColor Red
        }
    } else {
        Write-Host "Операционный журнал '$LogName' уже активен и ведет запись событий." -ForegroundColor Green
    }
} else {
    Write-Host "Журнал '$LogName' не найден в данной конфигурации ОС." -ForegroundColor Red
}
