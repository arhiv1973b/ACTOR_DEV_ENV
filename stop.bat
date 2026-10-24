@echo off
chcp 65001 > nul
echo ================================================================================
echo CASE-MACHERET: Остановка фонового портала (app_dashboard.py)
echo ================================================================================

powershell -Command "$procs = Get-CimInstance Win32_Process -Filter \"Name = 'python.exe' AND CommandLine LIKE '%app_dashboard.py%'\" ; if ($procs) { foreach($p in $procs) { Stop-Process -Id $p.ProcessId -Force; Write-Host '[+] Успешно остановлен процесс app_dashboard.py с PID:' $p.ProcessId -ForegroundColor Green } } else { Write-Host '[-] Активных процессов app_dashboard.py не найдено.' -ForegroundColor Yellow }"

echo ================================================================================
pause
