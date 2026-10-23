# MCP Audit and Repair Script for A©tor + Docker
# Author: Gordon
# A©tor Compatible Version

param(
    [switch]$AutoRepair,
    [string]$ReportPath = "mcp_audit_report_A©tor.txt"
)

# Initialize report
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report += "═══════════════════════════════════════════════════════"
$report += "MCP AUDIT REPORT — A©tor Edition — $timestamp"
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
    Log-Step "Part 1: Checking MCP Servers (A©tor)" "Info"
    $script:report += ""
    
    try {
        $mcpList = & gemini mcp list 2>&1
        Log-Step "MCP list retrieved." "Success"
        $script:report += $mcpList
        $script:report += ""
        
        $disconnected = $mcpList | Select-String "Disconnected"
        if ($disconnected) {
            Log-Step "Found disconnected MCP servers!" "Warning"
            return $false
        } else {
            Log-Step "All MCP servers connected." "Success"
            return $true
        }
    }
    catch {
        Log-Step "Error retrieving MCP list: $_" "Error"
        return $false
    }
}

function Check-Containers {
    Log-Step "Part 2: Checking Docker Containers" "Info"
    $script:report += ""
    
    try {
        $containers = & docker ps 2>&1
        if ($containers -match "Cannot connect") {
            Log-Step "Docker daemon not running!" "Error"
            return $false
        }
        Log-Step "Docker containers retrieved." "Success"
        $script:report += $containers
        return $true
    }
    catch {
        Log-Step "Error retrieving containers: $_" "Error"
        return $false
    }
}

function Check-Logs {
    Log-Step "Part 3: Checking Docker Logs" "Info"
    $script:report += ""
    
    try {
        $containers = & docker ps -q 2>&1
        if ($containers.Count -eq 0) {
            Log-Step "No running containers." "Warning"
            return $true
        }
        
        foreach ($container in $containers) {
            $logs = & docker logs $container 2>&1 | Select-Object -Last 20
            Log-Step "Logs for container: $($container)" "Info"
            $script:report += "--- $($container) ---"
            $script:report += $logs
        }
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
    $script:report += "END OF REPORT — A©tor Audit Complete"
    $script:report += "═══════════════════════════════════════════════════════"
    
    $script:report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved: $ReportPath" "Success"
}

# Main execution
Log-Step "Starting MCP Audit (A©tor Edition)" "Info"
$report += ""

$mcp_ok = Check-MCPServers
$docker_ok = Check-Containers
$logs_ok = Check-Logs

$report += ""
Log-Step "Generating report..." "Info"
Save-Report

Write-Host ""
Log-Step "Audit complete." "Info"
