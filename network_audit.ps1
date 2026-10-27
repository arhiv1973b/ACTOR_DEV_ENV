<#
.SYNOPSIS
    TI-ULA Network & Docker Security Audit Script
.DESCRIPTION
    Logs active listening ports, Docker networks, and container states to an audit file.
    Subject of Law: A©tor (A©t0r) | CASE-MACHERET-1997-2026
    Allowed Scope: UDHR 1948, Jus Cogens, Erga Omnes, Art. 4 Constitution of RM.
#>

$LogDir = "H:\ACTOR_DEV_ENV\reports"
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$LogFile = Join-Path $LogDir "network_audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
"=== TI-ULA NETWORK & CONTAINER AUDIT [$Timestamp] ===" | Out-File -FilePath $LogFile -Encoding utf8

"--- LISTENING PORTS ---" | Out-File -FilePath $LogFile -Append -Encoding utf8
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress, LocalPort, OwningProcess | Sort-Object LocalPort | Format-Table -AutoSize | Out-String | Out-File -FilePath $LogFile -Append -Encoding utf8

"--- DOCKER NETWORKS ---" | Out-File -FilePath $LogFile -Append -Encoding utf8
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker network ls --format "table {{.ID}}\t{{.Name}}\t{{.Driver}}\t{{.Scope}}" | Out-File -FilePath $LogFile -Append -Encoding utf8
    
    "--- DOCKER CONTAINERS ---" | Out-File -FilePath $LogFile -Append -Encoding utf8
    docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Ports}}" | Out-File -FilePath $LogFile -Append -Encoding utf8
} else {
    "Docker CLI not available." | Out-File -FilePath $LogFile -Append -Encoding utf8
}

"A©TOR_KEY=`"# [⚖ A©tor Declaration]`"" | Out-File -FilePath $LogFile -Append -Encoding utf8
Write-Host "Audit completed. Log saved to $LogFile" -ForegroundColor Green
