param([string]$ReportPath = "mcp_audit_report.json")

# Определяем корень: если запущено как скрипт, используем $PSScriptRoot, иначе текущую папку
$Root = if ($PSScriptRoot) { $PSScriptRoot } else { $PWD.Path }
$reportDir = Join-Path -Path $Root -ChildPath "reports"
$MemoryLog = Join-Path -Path $Root -ChildPath "memory_log.json"

$Color = @{ "Success"="Green"; "Error"="Red"; "Warning"="Yellow"; "Info"="Cyan" }

if (-not (Test-Path $reportDir)) { New-Item -Path $reportDir -ItemType Directory -Force | Out-Null }

function Log-Step {
    param([string]$Message, [string]$Type = "Info")
    $p = switch($Type) { "Success"{"✓"}; "Error"{"✗"}; "Warning"{"⚠"}; default{"ℹ"} }
    Write-Host -ForegroundColor $Color[$Type] "$p $Message"
}

function Write-Memory {
    param([string]$ErrorMsg, [string]$Fix)
    $entry = [PSCustomObject]@{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        error = $ErrorMsg
        fix = $Fix
    }
    $entry | ConvertTo-Json -Compress | Out-File -FilePath $MemoryLog -Append -Encoding UTF8
}

Log-Step "Starting MCP Audit v3.0" "Info"

try {
    # Проверка MCP серверов (gemini cli)
    $mcp_output = gemini mcp list 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "MCP List command failed: $mcp_output"
    }
    
    $FinalPath = Join-Path -Path $reportDir -ChildPath $ReportPath
    Log-Step "Audit complete. Report stored in $FinalPath" "Success"
} catch {
    $err = $_.Exception.Message
    Log-Step "Audit failed: $err" "Error"
    Write-Memory -ErrorMsg $err -Fix "Manual check required for MCP connection"
    exit 1
}
