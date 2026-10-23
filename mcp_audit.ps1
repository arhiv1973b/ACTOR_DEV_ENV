param(
    [switch]$AutoRepair,
    [string]$ReportPath = "mcp_audit_report.txt"
)

$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

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
    $color = switch ($Type) {
        "Success" { $ColorSuccess }
        "Error"   { $ColorError }
        "Warning" { $ColorWarning }
        "Info"    { $ColorInfo }
        default   { "White" }
    }
    Write-Host "$prefix $Message" -ForegroundColor $color
    $script:report += "[$Type] $Message"
}

function Check-MCPServers {
    Log-Step "Part 1: Checking MCP Servers" "Info"
    $script:report += ""
    
    try {
        $mcpList = & gemini mcp list 2>&1
        Log-Step "MCP list retrieved successfully." "Success"
        $script:report += $mcpList
        $script:report += ""
        
        $disconnected = $mcpList | Select-String "Disconnected"
        if ($disconnected) {
            Log-Step "Found disconnected MCP servers!" "Warning"
            $script:report += "Disconnected servers found."
            return $false
        } else {
            Log-Step "All MCP servers appear connected." "Success"
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
        if ($containers -match "Cannot connect to Docker daemon") {
            Log-Step "Docker daemon not running!" "Error"
            $script:report += "Docker daemon is not running."
            return $false
        }
        Log-Step "Docker containers retrieved." "Success"
        $script:report += $containers
        $script:report += ""
        
        $runningCount = ($containers | Measure-Object -Line).Lines - 1
        Log-Step "Running containers: $runningCount" "Info"
        return $true
    }
    catch {
        Log-Step "Error retrieving containers: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Check-Logs {
    Log-Step "Part 3: Checking Docker Logs" "Info"
    $script:report += ""
    
    try {
        $containers = & docker ps -q 2>&1
        if ($containers.Count -eq 0) {
            Log-Step "No running containers found." "Warning"
            $script:report += "No running containers to check logs."
            return $true
        }
        
        foreach ($container in $containers) {
            $logs = & docker logs $container 2>&1 | Select-Object -Last 20
            Log-Step "Logs for container $container (last 20 lines):" "Info"
            $script:report += "--- Logs for $container ---"
            $script:report += $logs
            $script:report += ""
            
            if ($logs -match "ENOENT|stat.*run|Connection refused") {
                Log-Step "Potential errors detected in logs!" "Warning"
            }
        }
        return $true
    }
    catch {
        Log-Step "Error retrieving logs: $_" "Error"
        $script:report += "Error: $_"
        return $false
    }
}

function Check-MCPProfile {
    Log-Step "Part 4: Checking MCP Profile Configuration" "Info"
    $script:report += ""
    
    try {
        $mcpList = & gemini mcp list 2>&1
        if ($mcpList -match "terminal_control|ti_ula") {
            Log-Step "MCP server running with limited profile (terminal_control/ti_ula)." "Warning"
            $script:report += "Limited profile detected. Recommend switching to 'full' profile."
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

function Test-MCPTools {
    Log-Step "Part 6: Testing MCP Tools" "Info"
    $script:report += ""
    
    try {
        $tools = & gemini tools 2>&1
        if ($tools -match "filesystem|search|prompt") {
            Log-Step "MCP tools available and responding." "Success"
            $script:report += $tools
            return $true
        } else {
            Log-Step "No standard MCP tools detected." "Warning"
            $script:report += $tools
            return $false
        }
    }
    catch {
        Log-Step "Error testing tools: $_" "Error"
        return $false
    }
}

function Save-Report {
    $script:report += ""
    $script:report += "═══════════════════════════════════════════════════════"
    $script:report += "END OF REPORT"
    $script:report += "═══════════════════════════════════════════════════════"
    
    $script:report | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Log-Step "Report saved to: $ReportPath" "Success"
}

Log-Step "Starting MCP Audit and Repair Sequence" "Info"
$report += ""

$mcp_ok = Check-MCPServers
$docker_ok = Check-Containers
$logs_ok = Check-Logs
$profile_ok = Check-MCPProfile
$tools_ok = Test-MCPTools

$report += ""
Log-Step "Generating final report..." "Info"
Save-Report

$report += ""
$report += "AUDIT SUMMARY:"
$report += "─────────────────────────────────────"
$report | Select-Object -Last 5 | ForEach-Object { Write-Host $_ }

Write-Host ""
Log-Step "Audit complete. Report: $ReportPath" "Info"
& H:\ACTOR_DEV_ENV\audit_sync.ps1 -SourceFile $ReportPath
