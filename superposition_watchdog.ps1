# Jus Cogens Self-Healing Watchdog (Windows PowerShell)
# Signature: # ⚖ A©tor Declaration

$ScriptPath = "jus_cogens_heartbeat.py"

while ($true) {
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*$ScriptPath*" }
    if (-not $process) {
        Write-Output "[WATCHDOG] Heartbeat miner down or not found! Restarting in background..."
        Start-Process python -ArgumentList $ScriptPath -WindowStyle Hidden
    }
    Start-Sleep -Seconds 60
}
