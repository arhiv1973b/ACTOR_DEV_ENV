# MCP Audit and Repair Script for Docker
# Author: Gordon
# Description: Audits MCP server status, Docker containers, and logs. Auto-repairs if disconnected.

param(
    [switch]$AutoRepair,
    [string]$ReportPath = "mcp_audit_report.txt"
)

# Colors
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

# Initialize report
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$report += "═══════════════════════════════════════════════════════"
$report += "MCP AUDIT REPORT — $timestamp"
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
    Write-Host "$prefix $Message" -ForegroundColor $(
        switch ($Type) {
            "Success" { $ColorSuccess }
            "Error"   { $ColorError }
            "Warning" { $ColorWarning }
            "Info"    { $ColorInfo }
            default   { "White" }
        }
    )
    $report += "[$Type] $Message"
}

function Check-MCPServers {
    Log-Step "Part 1: Checking MCP Servers" "Info"
    $report += ""
    
    try {
        $mcpList = & gemini mcp list 2>&1
        Log-Step "MCP list retrieved successfully." "Success"
        $report += $mcpList
        $report += ""
        
        # Parse output to check for Connected/Disconnected
        $disconnected = $mcpList | Select-String "Disconnected"
        if ($disconnected) {
            Log-Step "Found disconnected MCP servers!" "Warning"
            $report += "Disconnected servers found."
            return $false
        } else {
            Log-Step "All MCP servers appear connected." "Success"
            return $true
        }
    }
    catch {
        Log-Step "Error retrieving MCP list: $_" "Error"
        $report += "Error: $_"
        return $false
    }
}

function Check-Containers {
    Log-Step "Part 2: Checking Docker Containers" "Info"
    $report += ""
    
    try {
        $containers = & docker ps 2>&1
        if ($containers -match "Cannot connect to Docker daemon") {
            Log-Step "Docker daemon not running!" "Error"
            $report += "Docker daemon is not running."
            return $false
        }
        Log-Step "Docker containers retrieved." "Success"
        $report += $containers
        $report += ""
        
        $runningCount = ($containers | Measure-Object -Line).Lines - 1
        Log-Step "Running containers: $runningCount" "Info"
        return $true
    }
    catch {
        Log-Step "Error retrieving containers: $_" "Error"
        $report += "Error: $_"
        return $false
    }
}

function Check-Logs {
    Log-Step "Part 3: Checking Docker Logs" "Info"
    $report += ""
    
    try {
        $containers = & docker ps -q 2>&1
        if ($containers.Count -eq 0) {
            Log-Step "No running containers found." "Warning"
            $report += "No running containers to check logs."
            return $true
        }
        
        foreach ($container in $containers) {
            $logs = & docker logs $container 2>&1 | Select-Object -Last 20
            Log-Step "Logs for container $container (last 20 lines):" "Info"
            $report += "--- Logs for $container ---"
            $report += $logs
            $report += ""
            
            # Check for common errors
            if ($logs -match "ENOENT|stat.*run|Connection refused") {
                Log-Step "Potential errors detected in logs!" "Warning"
            }
        }
        return $true
    }
    catch {
        Log-Step "Error retrieving logs: $_" "Error"
        $report += "Error: $_"
        return $false
    }
}

function Check-MCPProfile {
    Log-Step "Part 4: Checking MCP Profile Configuration" "Info"
    $report += ""
    
    try {
        $mcpList = & gemini mcp list 2>&1
        if ($mcpList -match "terminal_control|ti_ula") {
            Log-Step "MCP server running with limited profile (terminal_control/ti_ula)." "Warning"
            $report += "Limited profile detected. Recommend switching to 'full' profile."
            return $false
        }
        Log-Step "Profile check passed (or not detected)." "Success"
        return $true
    }
    catch {
        Log-Step "Error checking profile: $_" "Error"
        return $false
    }
}

function Repair-MCP {
    Log-Step "Part 5: Auto-Repair MCP" "Info"
    $report += ""
    
    if (-not $AutoRepair) {
        Log-Step "Auto-repair disabled. Use -AutoRepair flag to enable." "Warning"
        return $false
    }
    
    try {
        Log-Step "Removing disconnected MCP server..." "Info"
        & gemini mcp remove MCP_DOCKER 2>&1 | ForEach-Object { $report += $_ }
        Start-Sleep -Seconds 2
        
        Log-Step "Re-adding MCP server with 'full' profile..." "Info"
        $addCmd = 'gemini mcp add MCP_DOCKER "docker run -i --rm -v H:\ACTOR_DEV_ENV\apostille-mirror:/run mcp/filesystem /run" --profile full'
        & cmd /c $addCmd 2>&1 | ForEach-Object { $report += $_ }
        Start-Sleep -Seconds 3
        
        Log-Step "MCP server re-added. Checking status..." "Info"
        $mcpList = & gemini mcp list 2>&1
        $report += $mcpList
        
        if ($mcpList -match "Connected") {
            Log-Step "MCP repair successful!" "Success"
            return $true
        } else {
            Log-Step "MCP status still disconnected after repair attempt." "Warning"
            return $false
        }
    }
    catch {
        Log-Step "Error during repair: $_" "Error"
        $report += "Error: $_"
        return $false
    }
}

function Test-MCPTools {
    Log-Step "Part 6: Testing MCP Tools" "Info"
    $report += ""
    
    try {
        $tools = & gemini tools 2>&1
        if ($tools -match "filesystem|search|prompt") {
            Log-Step "MCP tools available and responding." "Success"
            $report += $tools
            return $true
        } else {
            Log-Step "No standard MCP tools detected." "Warning"
            $report += $tools
            return $false
        }
    }
    catch {
        Log-Step "Error testing tools: $_" "Error"
        return $false
    }
}

function Save-Report {
    $report += ""
    $report += "═══════════════════════════════════════════════════════"
    $report += "END OF REPORT"
    $report += "═══════════════════════════════════════════════════════"
    
    $report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved to: $ReportPath" "Success"
}

# ─────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────

Log-Step "Starting MCP Audit and Repair Sequence" "Info"
$report += ""

# Execute all checks
$mcp_ok = Check-MCPServers
$docker_ok = Check-Containers
$logs_ok = Check-Logs
$profile_ok = Check-MCPProfile
$tools_ok = Test-MCPTools

# Auto-repair if needed
if (-not $mcp_ok -and $AutoRepair) {
    $repair_ok = Repair-MCP
}

# Save report
$report += ""
Log-Step "Generating final report..." "Info"
Save-Report

# Summary
$report += ""
$report += "AUDIT SUMMARY:"
$report += "─────────────────────────────────────"
$report | Select-Object -Last 5 | ForEach-Object { Write-Host $_ }

Write-Host ""
Log-Step "Audit complete. Report: $ReportPath" "Info"
