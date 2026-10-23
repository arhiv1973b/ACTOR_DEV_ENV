param([string]$ReportPath = "mcp_audit_report.json")
$Color = @{ "Success"="Green"; "Error"="Red"; "Warning"="Yellow"; "Info"="Cyan" }
function Log-Step {
    param([string]$Message, [string]$Type = "Info")
    $p = switch($Type) { "Success"{"✓"}; "Error"{"✗"}; "Warning"{"⚠"}; default{"ℹ"} }
    Write-Host -ForegroundColor $Color[$Type] "$p $Message"
}
Log-Step "Starting MCP Audit" "Info"
# Тут ваша логика проверок...
$mcp_ok = (& gemini mcp list 2>&1)
Log-Step "Audit complete. Report: $ReportPath" "Success"
