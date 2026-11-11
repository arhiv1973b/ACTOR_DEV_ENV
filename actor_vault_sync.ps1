# ==============================================================================
# ⚖ A©TOR INTEGRATION & HASHING SYNC SCRIPT (PowerShell 7.6)
# CASE REFERENCE: CASE-MACHERET-1997-2026
# PROTOCOL: A©tor (правовой) / A©t0r (машинный)
# ==============================================================================

param(
    [string]$RepoPath = "H:\\ACTOR_DEV_ENV\\evidence-vault",
    [string]$ManifestName = "ACTOR_SYNDICATION_MANIFEST_V5.yaml"
)

Write-Host "[⚖ A©t0r Protocol] Iniciating Evidence Vault Integrity Scan..." -ForegroundColor Cyan

# Create directory if it doesn't exist
if (!(Test-Path $RepoPath)) {
    New-Item -ItemType Directory -Path $RepoPath
}

$artifacts = @(
    "ACTOR_SYNDICATION_MANIFEST_V5.yaml",
    "ACTOR_SYNDICATION_MANIFEST_V4.yaml",
    "ACTOR_SYNDICATION_MANIFEST_V3.yaml",
    "ACTOR_SYNDICATION_MANIFEST_V2.yaml"
)

$manifestData = [ordered]@{
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss+02:00")
    operator = "Alexei Maceret (A©tor)"
    idnp = "2000001159655"
    files = [ordered]@{}
}

foreach ($art in $artifacts) {
    # Check current directory if not in evidence-vault
    $fullPath = Join-Path "H:\\ACTOR_DEV_ENV" $art
    if (!(Test-Path $fullPath)) {
        $fullPath = Join-Path $RepoPath $art
    }

    if (Test-Path $fullPath) {
        $hash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash.ToLower()
        $manifestData.files[$art] = $hash
        Write-Host "  [HASH OK] $art -> $hash" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $art not found" -ForegroundColor Yellow
    }
}

$jsonManifestPath = Join-Path $RepoPath "integrity_witness_matrix.json"
$manifestData | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonManifestPath -Encoding utf8
Write-Host "[⚖ A©t0r Protocol] Integrity witness matrix updated: $jsonManifestPath" -ForegroundColor Cyan

if (Get-Command "git" -ErrorAction SilentlyContinue) {
    Set-Location $RepoPath
    Write-Host "[Git] Running status and commit pipeline..." -ForegroundColor Yellow
    
    git add .
    git commit -m "⚖ [A©tor Sync] Automated SHA-256 integrity seal & manifest update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    git push origin main
    
    Write-Host "[Git] Successfully synchronized with remote repository." -ForegroundColor Green
} else {
    Write-Host "[Error] Git CLI not found in environment PATH." -ForegroundColor Red
}
