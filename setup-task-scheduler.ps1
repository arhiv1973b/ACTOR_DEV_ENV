<#
.SYNOPSIS
    Registers a Windows Scheduled Task to run repository audit and sync daily at 02:00.
#>

$TaskName = "ActorDevEnvDailyAudit"
$ScriptPath = "$PSScriptRoot\audit_sync_all_repos.ps1"
$WorkingDirectory = $PSScriptRoot

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -AutoCommit -AutoPush" -WorkingDirectory $WorkingDirectory
$Trigger = New-ScheduledTaskTrigger -Daily -At 02:00AM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force

Write-Host "Windows Scheduled Task '$TaskName' registered successfully to run daily at 02:00." -ForegroundColor Green
