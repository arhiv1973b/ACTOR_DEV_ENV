$ScriptToRun = "H:\ACTOR_DEV_ENV\mcp_audit_v2.ps1"
if (-not (Test-Path $ScriptToRun)) { Write-Error "Файл отсутствует!"; return }
& $ScriptToRun
Read-Host "Нажмите Enter для завершения..."
