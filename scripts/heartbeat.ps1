# Heartbeat script for ACTOR_DEV_ENV evidence repository
# Ensures the branch evidence-mvd-dec-2025 is synchronized and "alive"
$repoPath = "H:\ACTOR_DEV_ENV"
$logFile = "H:\ACTOR_DEV_ENV\logs\heartbeat.log"

try {
    Set-Location $repoPath
    # Sync with remote
    git fetch origin
    git pull origin evidence-mvd-dec-2025
    git push origin evidence-mvd-dec-2025
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content $logFile "$timestamp: Heartbeat successful. Evidence branch synchronized."
} catch {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content $logFile "$timestamp: Heartbeat FAILED. Error: $_"
}
