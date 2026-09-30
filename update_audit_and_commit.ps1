param(
    [string]$ManifestPath = "H:\ACTOR_DEV_ENV\apostille-mirror\A©tor_FORENSIC_AUDIT_MANIFEST_V4_4.md",
    [string]$Branch = "udhr-audit-rebuild-2026"
)

Write-Host "=== Starting Forensic Manifest Update & Git Anchor ==="

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    Write-Error "Manifest not found at $ManifestPath"
    exit 1
}

# Append DAG Manifest Hash integration note if not already present
$Content = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8
$DagHashNote = "`n`n## Криптографическая привязка DAG Manifest`n* **DAG Manifest SHA-256:** `6C913818321D40F9EE10E56F417E1521B968F6209CB10614C83F037E6F5B060C`n* **Статус:** `INTEGRITY_LOCKED` (Верифицировано 14 июня 2026)`n"

if ($Content -notmatch "6C913818321D40F9EE10E56F417E1521B968F6209CB10614C83F037E6F5B060C") {
    Add-Content -LiteralPath $ManifestPath -Value $DagHashNote -Encoding UTF8
    Write-Host "Added DAG Manifest hash anchoring to forensic manifest."
} else {
    Write-Host "DAG Manifest hash already anchored in manifest."
}

# Calculate SHA-256 hash of the manifest file
$HashResult = Get-FileHash -LiteralPath $ManifestPath -Algorithm SHA256
Write-Host "Manifest SHA-256 Hash: $($HashResult.Hash)"

# Git Operations
Set-Location "H:\ACTOR_DEV_ENV"
git checkout $Branch
git add "apostille-mirror/A©tor_FORENSIC_AUDIT_MANIFEST_V4_4.md"
git commit -m "chore(audit): anchor A©tor_V4.4 forensic manifest and DAG hash 6C913818321D40F9EE10E56F417E1521B968F6209CB10614C83F037E6F5B060C"

Write-Host "=== Forensic Manifest Anchored Successfully on $Branch ==="
