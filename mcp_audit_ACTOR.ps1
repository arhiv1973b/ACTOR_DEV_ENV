# MCP Audit and Repair Script for ACTOR + Docker
# Author: Gordon
# ACTOR Compatible Version

param(
    [switch]$AutoRepair,
    [string]$ReportPath = "mcp_audit_report.txt"
)

# Initialize report
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report += "========================================================="
$report += "MCP AUDIT REPORT - ACTOR Edition - $timestamp"
$report += "========================================================="
$report += ""

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

function Check-MCPServers {
    Log-Step "Part 1: Checking MCP Servers" "Info"
    $script:report += ""
    
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
            Log-Step "All MCP servers connected." "Success"
            return $true
        }
    }
    catch {
        Log-Step "Error retrieving MCP list: $_" "Error"
        $script:report += "Error: $_"
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
        $script:report += "--- Running Containers ---"
        $script:report += $containers
        $script:report += ""
        return $true
    }
    catch {
        Log-Step "Error retrieving containers: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Check-AllContainers {
    Log-Step "Part 2b: Checking All Containers (including stopped)" "Info"
    $script:report += ""
    
    try {
        $allContainers = & docker ps -a 2>&1
        $script:report += "--- All Containers ---"
        $script:report += $allContainers
        $script:report += ""
        return $true
    }
    catch {
        Log-Step "Error retrieving all containers: $_" "Error"
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
            $script:report += "No running containers to check logs."
            return $true
        }
        
        $script:report += "--- Container Logs ---"
        foreach ($container in $containers) {
            $shortId = $container.Substring(0, 12)
            $logs = & docker logs $shortId 2>&1 | Select-Object -Last 30
            $script:report += ""
            $script:report += "Container: $shortId"
            $script:report += $logs
        }
        return $true
    }
    catch {
        Log-Step "Error retrieving logs: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Check-MCPStatus {
    Log-Step "Part 4: Checking MCP Detailed Status" "Info"
    $script:report += ""
    
    try {
        $status = & gemini mcp list 2>&1
        $script:report += "--- MCP Status Details ---"
        $script:report += $status
        $script:report += ""
        return $true
    }
    catch {
        Log-Step "Error checking MCP status: $_" "Error"
        return $false
    }
}

function Save-Report {
    $script:report += ""
    $script:report += "========================================================="
    $script:report += "END OF REPORT - ACTOR Audit Complete"
    $script:report += "Report generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $script:report += "========================================================="
    
    $script:report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved: $ReportPath" "Success"
    
    # Also display path
    $fullPath = (Get-Item $ReportPath).FullName
    Write-Host "Full path: $fullPath"
}

# Main execution
Log-Step "Starting MCP Audit (ACTOR Edition)" "Info"
Write-Host "Current directory: $(Get-Location)"
$report += ""

$mcp_ok = Check-MCPServers
$docker_ok = Check-Containers
$all_ok = Check-AllContainers
$logs_ok = Check-Logs
$status_ok = Check-MCPStatus

$report += ""
Log-Step "Generating report..." "Info"
Save-Report

Write-Host ""
Log-Step "Audit complete." "Info"
