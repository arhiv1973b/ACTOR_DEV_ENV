# Unified MCP Audit Script
# Harmonized for A©tor, ACTOR, and Standard Environments
# Features: Container Checks (All), Standardized Logging, Robust Error Handling

param(
    [switch]$AutoRepair,
    [string]$ReportPath = "mcp_audit_unified_report.txt"
)

# Initialize report
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report += "═══════════════════════════════════════════════════════"
$report += "UNIFIED MCP AUDIT REPORT — $timestamp"
$report += "═══════════════════════════════════════════════════════"
$report += ""

function Log-Step {
    param([string]$Message, [string]$Type = "Info")
    $prefix = switch ($Type) {
        "Success" { "✓" }
        "Error"   { "✗" }
        "Warning" { "⚠" }
        "Info"    { "ℹ" }
        default   { "→" }
    }
    Write-Host "$prefix $Message"
    $script:report += "[$Type] $Message"
}

function Check-MCPServers {
    Log-Step "Part 1: Checking MCP Servers" "Info"
    
    try {
        $mcpList = & gemini mcp list 2>&1
        Log-Step "MCP list retrieved." "Success"
        $script:report += "--- MCP Servers ---"
        $script:report += $mcpList
        $script:report += ""
        
        $disconnected = $mcpList | Select-String "Disconnected"
        if ($disconnected) {
            Log-Step "Found disconnected MCP servers!" "Warning"
            return $false
        } else {
            Log-Step "All MCP servers appear connected." "Success"
            return $true
        }
    }
    catch {
        Log-Step "Error retrieving MCP list: $_" "Error"
        return $false
    }
}

function Check-AllContainers {
    Log-Step "Part 2: Checking All Containers (incl. stopped)" "Info"
    
    try {
        $allContainers = & docker ps -a 2>&1
        if ($allContainers -match "Cannot connect") {
            Log-Step "Docker daemon not running!" "Error"
            return $false
        }
        
        $script:report += "--- Running/Stopped Containers ---"
        $script:report += $allContainers
        $script:report += ""
        Log-Step "Container status retrieved." "Success"
        return $true
    }
    catch {
        Log-Step "Error retrieving containers: $_" "Error"
        return $false
    }
}

function Check-Logs {
    Log-Step "Part 3: Checking Docker Logs" "Info"
    
    try {
        $containers = & docker ps -q 2>&1
        if ($containers.Count -eq 0) {
            Log-Step "No running containers." "Warning"
            return $true
        }
        
        $script:report += "--- Container Logs (Last 20 lines) ---"
        foreach ($container in $containers) {
            $shortId = $container.Substring(0, 12)
            $logs = & docker logs $shortId 2>&1 | Select-Object -Last 20
            
            $script:report += "Container: $shortId"
            $script:report += $logs
            $script:report += ""
        }
        Log-Step "Logs collected for all running containers." "Success"
        return $true
    }
    catch {
        Log-Step "Error retrieving logs: $_" "Error"
        return $false
    }
}

function Save-Report {
    $script:report += ""
    $script:report += "═══════════════════════════════════════════════════════"
    $script:report += "END OF UNIFIED AUDIT REPORT"
    $script:report += "Report generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $script:report += "═══════════════════════════════════════════════════════"
    
    $script:report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved: $ReportPath" "Success"
}

# Main execution
Log-Step "Starting Unified MCP Audit" "Info"
$mcp_ok = Check-MCPServers
$containers_ok = Check-AllContainers
$logs_ok = Check-Logs

Log-Step "Generating report..." "Info"
Save-Report

Log-Step "Audit complete." "Success"
