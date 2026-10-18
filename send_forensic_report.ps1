# send_forensic_report.ps1
param(
    [string]$ReportFile = "artifacts/reabilitare/forensic_capture_ledger.json",
    [string]$SecretKey = "supersecretkey",
    [string]$BearerToken = $env:FORENSIC_BEARER_TOKEN
)

$WebhookUrl = $env:FORENSIC_WEBHOOK_URL
if (-not $WebhookUrl) { Write-Error "FORENSIC_WEBHOOK_URL not set"; exit 1 }

$Body = Get-Content $ReportFile -Raw
$Bytes = [System.Text.Encoding]::UTF8.GetBytes($Body)

$HMAC = New-Object System.Security.Cryptography.HMACSHA256
$HMAC.Key = [System.Text.Encoding]::UTF8.GetBytes($SecretKey)
$Signature = ($HMAC.ComputeHash($Bytes) | ForEach-Object ToString x2) -join ""

$Headers = @{
    "Content-Type" = "application/json"
}
if ($BearerToken) {
    $Headers["Authorization"] = "Bearer $BearerToken"
}

$Payload = @{
    report = $Body
    signature = $Signature
} | ConvertTo-Json

Invoke-RestMethod -Uri $WebhookUrl -Method Post -Headers $Headers -Body $Payload | Out-Null
Write-Host "[OK] Forensic report sent successfully with HMAC signature and Bearer auth."
