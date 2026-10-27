# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$LogFolder = $env:USERPROFILE
$DaysThreshold = 30
$CutoffDate = (Get-Date).AddDays(-$DaysThreshold)

Write-Host "Сканирование каталога '$LogFolder' на наличие CSV-логов старше $DaysThreshold дней ($($CutoffDate.ToString('yyyy-MM-dd')))..." -ForegroundColor Cyan

$TargetLogs = Get-ChildItem -Path $LogFolder -Filter "*Audit*.csv" -File | 
              Where-Object { $_.LastWriteTime -lt $CutoffDate }

if ($TargetLogs) {
    foreach ($File in $TargetLogs) {
        try {
            Remove-Item -Path $File.FullName -Force
            Write-Host "Удален устаревший архивный лог: $($File.Name) (Дата изменения: $($File.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))" -ForegroundColor Yellow
        } catch {
            Write-Host "ОШИБКА: Не удалось удалить файл $($File.Name) — $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    Write-Host "Ротация успешно завершена. Очищено файлов: $($TargetLogs.Count)" -ForegroundColor Green
} else {
    Write-Host "Устаревшие файлы аудита (старше $DaysThreshold дней) не найдены." -ForegroundColor Green
}
