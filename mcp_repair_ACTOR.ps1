# MCP Repair and Fix Script for ACTOR + Docker
# Author: Gordon
# ACTOR Compatible Version with Auto-Repair

param(
    [switch]$AutoRepair = $false,
    [switch]$DryRun = $true,
    [string]$ReportPath = "mcp_repair_report.txt"
)

# Initialize report
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report += "========================================================="
$report += "MCP REPAIR REPORT - ACTOR Edition - $timestamp"
$report += "========================================================="
$report += ""

if ($DryRun -and -not $AutoRepair) {
    $report += "[DRY-RUN MODE] No changes will be made. Use -AutoRepair to execute repairs."
    $report += ""
}

if ($AutoRepair -and -not $DryRun) {
    $report += "[REPAIR MODE] Executing fixes..."
    $report += ""
}

function Log-Step {
    param([string]$Message, [string]$Type = "Info")
    $prefix = switch ($Type) {
        "Success" { "[OK]" }
        "Error"   { "[ERR]" }
        "Warning" { "[WARN]" }
        "Info"    { "[INFO]" }
        default   { "[*]" }
    }
    Write-Host "$prefix $Message"
    $script:report += "$prefix $Message"
}

function Check-DockerNetworks {
    Log-Step "Part 1: Checking Docker Networks" "Info"
    $script:report += ""
    
    try {
        $networks = & docker network ls 2>&1
        $script:report += "--- Docker Networks ---"
        $script:report += $networks
        $script:report += ""
        
        $hasActorNetwork = $networks | Select-String "actor-network"
        if ($hasActorNetwork) {
            Log-Step "ACTOR network exists." "Success"
            return $true
        } else {
            Log-Step "ACTOR network NOT found!" "Warning"
            return $false
        }
    }
    catch {
        Log-Step "Error checking networks: $_" "Error"
        return $false
    }
}

function Repair-NgninxHealthcheck {
    Log-Step "Part 2: Repairing actor_site (nginx) - Read-Only FS" "Info"
    $script:report += ""
    
    try {
        $container = "actor_site"
        
        # Check current status
        $status = & docker inspect $container --format='{{.State.Health.Status}}' 2>&1
        $script:report += "Current status: $status"
        
        if ($DryRun) {
            Log-Step "[DRY-RUN] Would stop and remove $container" "Info"
            $script:report += "Planned actions:"
            $script:report += "  1. docker stop $container"
            $script:report += "  2. docker rm $container"
            $script:report += "  3. docker run -d --name $container -p 8085:80 -p 8444:443 nginx:alpine"
            return $false
        }
        
        if ($AutoRepair) {
            Log-Step "Stopping $container..." "Info"
            & docker stop $container 2>&1 | ForEach-Object { $script:report += $_ }
            Start-Sleep -Seconds 2
            
            Log-Step "Removing $container..." "Info"
            & docker rm $container 2>&1 | ForEach-Object { $script:report += $_ }
            
            Log-Step "Recreating $container with fresh nginx..." "Info"
            & docker run -d --name $container -p 8085:80 -p 8444:443 nginx:alpine 2>&1 | ForEach-Object { $script:report += $_ }
            Start-Sleep -Seconds 3
            
            $newStatus = & docker inspect $container --format='{{.State.Health.Status}}' 2>&1
            $script:report += "New status: $newStatus"
            
            if ($newStatus -match "healthy|running") {
                Log-Step "$container repaired successfully!" "Success"
                return $true
            } else {
                Log-Step "$container repair incomplete." "Warning"
                return $false
            }
        }
    }
    catch {
        Log-Step "Error repairing nginx: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Repair-ActorNetwork {
    Log-Step "Part 3: Creating/Fixing ACTOR Network" "Info"
    $script:report += ""
    
    try {
        # Check if network exists
        $exists = & docker network ls 2>&1 | Select-String "actor-network"
        
        if (-not $exists) {
            if ($DryRun) {
                Log-Step "[DRY-RUN] Would create actor-network" "Info"
                $script:report += "Planned action: docker network create actor-network"
                return $false
            }
            
            if ($AutoRepair) {
                Log-Step "Creating actor-network..." "Info"
                & docker network create actor-network 2>&1 | ForEach-Object { $script:report += $_ }
                Log-Step "Network created." "Success"
                return $true
            }
        } else {
            Log-Step "actor-network already exists." "Success"
            return $true
        }
    }
    catch {
        Log-Step "Error managing network: $_" "Error"
        return $false
    }
}

function Reconnect-ContainersToNetwork {
    Log-Step "Part 4: Reconnecting containers to actor-network" "Info"
    $script:report += ""
    
    try {
        $containers = @("actor_robot", "actor_ollama", "act0r-ollama")
        
        foreach ($container in $containers) {
            $exists = & docker ps -a 2>&1 | Select-String $container
            
            if ($exists) {
                if ($DryRun) {
                    Log-Step "[DRY-RUN] Would reconnect $container to actor-network" "Info"
                    $script:report += "Planned actions for $($container):"
                    $script:report += "  1. Disconnect from bridge"
                    $script:report += "  2. Connect to actor-network"
                } else {
                    Log-Step "Reconnecting $($container)..." "Info"
                    
                    # Try to disconnect from bridge first (ignore errors)
                    & docker network disconnect bridge $container 2>&1 | Out-Null
                    
                    # Connect to actor-network
                    & docker network connect actor-network $container 2>&1 | ForEach-Object { $script:report += $_ }
                    
                    Log-Step "$($container) reconnected." "Success"
                }
            }
        }
        return $true
    }
    catch {
        Log-Step "Error reconnecting containers: $_" "Error"
        return $false
    }
}

function Check-GitBranch {
    Log-Step "Part 5: Checking Git Branch in aytor-sentinel" "Info"
    $script:report += ""
    
    try {
        $branches = & docker exec aytor-sentinel git branch -a 2>&1
        $script:report += "--- Git Branches ---"
        $script:report += $branches
        $script:report += ""
        
        $hasBranch = $branches | Select-String "Actor-IP-Protection"
        if ($hasBranch) {
            Log-Step "Branch 'Actor-IP-Protection' exists." "Success"
            return $true
        } else {
            Log-Step "Branch 'Actor-IP-Protection' NOT found!" "Warning"
            $script:report += "Available branches:"
            $script:report += $branches
            return $false
        }
    }
    catch {
        Log-Step "Error checking git branch: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Save-Report {
    $script:report += ""
    $script:report += "========================================================="
    $script:report += "END OF REPAIR REPORT - ACTOR Edition"
    $script:report += "Report mode: $(if ($DryRun) { 'DRY-RUN' } else { 'REPAIR' })"
    $script:report += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $script:report += "========================================================="
    
    $script:report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved: $ReportPath" "Success"
}

# ─────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────

Log-Step "Starting MCP Repair (ACTOR Edition)" "Info"
Write-Host "Current directory: $(Get-Location)"
Write-Host "Mode: $(if ($DryRun) { 'DRY-RUN (no changes)' } else { 'REPAIR (executing fixes)' })"
$report += ""

# Run all checks
$networks_ok = Check-DockerNetworks
$nginx_ok = Repair-NgninxHealthcheck
$network_ok = Repair-ActorNetwork
$reconnect_ok = Reconnect-ContainersToNetwork
$git_ok = Check-GitBranch

$report += ""
Log-Step "Generating repair report..." "Info"
Save-Report

Write-Host ""
Log-Step "Repair sequence complete." "Info"

if ($DryRun) {
    Write-Host ""
    Write-Host "To execute repairs, run:"
    Write-Host "  .\mcp_repair_ACTOR.ps1 -AutoRepair -DryRun:`$false"
    Write-Host ""
}
