# Audit Synchronization and Integrity Protocol
# Moves audit reports to forensic storage and generates hash for integrity

param(
    [string]$SourceFile = "mcp_audit_unified_report.txt",
    [string]$TargetDir = "H:\ACTOR_DEV_ENV\apostille-mirror\forensic_reports"
)

if (-not (Test-Path $SourceFile)) {
    Write-Error "Source file $SourceFile not found."
    exit 1
}

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$FileName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)
$NewPath = Join-Path $TargetDir "$FileName`_$Timestamp.txt"

# Move the file
Move-Item -Path $SourceFile -Destination $NewPath -Force
Write-Host "Moved report to: $NewPath"

# Generate hash for integrity
$Hash = Get-FileHash -Path $NewPath -Algorithm SHA256
$HashFile = "$NewPath.sha256"
$Hash.Hash | Out-File -FilePath $HashFile -Encoding UTF8
Write-Host "Integrity hash generated: $HashFile"
Write-Host "Hash: $($Hash.Hash)"
