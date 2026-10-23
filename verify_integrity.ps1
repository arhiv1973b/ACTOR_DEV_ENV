# Forensic Audit Integrity Verification Script
# Validates files in the provided manifest against their documented SHA256 hashes.

param(
    [Parameter(Mandatory=$true)]
    [string]$ManifestPath
)

if (-not (Test-Path $ManifestPath)) {
    Write-Error "Manifest file not found: $ManifestPath"
    exit 1
}

$manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json

Write-Host "Verifying forensic integrity for: $($manifest.case_id)" -ForegroundColor Cyan

$allValid = $true

foreach ($nodeName in $manifest.evidence_nodes.psobject.Properties.Name) {
    $node = $manifest.evidence_nodes.$nodeName
    $filePath = $node.path
    $expectedHash = $node.sha256

    if (-not (Test-Path $filePath)) {
        Write-Host "✗ File not found: $filePath" -ForegroundColor Red
        $allValid = $false
        continue
    }

    $fileHash = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
    
    if ($fileHash -eq $expectedHash) {
        Write-Host "✓ Verified: $nodeName ($filePath)" -ForegroundColor Green
    } else {
        Write-Host "✗ Hash Mismatch: $nodeName ($filePath)" -ForegroundColor Red
        Write-Host "  Expected: $expectedHash" -ForegroundColor Red
        Write-Host "  Actual:   $fileHash" -ForegroundColor Red
        $allValid = $false
    }
}

if ($allValid) {
    Write-Host "Integrity verification successful." -ForegroundColor Green
} else {
    Write-Host "Integrity verification FAILED." -ForegroundColor Red
    exit 1
}
