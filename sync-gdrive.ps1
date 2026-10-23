<#
.SYNOPSIS
    Sync H:\ACTOR_DEV_ENV evidence files to Google Drive CASE-MACHERET-1997-2026 folder
    and update SHA-256 manifest + commit to GitHub.
#>

$ErrorActionPreference = "Stop"
$rclone     = "C:\Users\arhiv\AppData\Local\Microsoft\WinGet\Links\rclone.exe"
$LocalDir   = "H:\ACTOR_DEV_ENV"
$RemotePath = "gdrive:CASE-MACHERET-1997-2026"
$LogFile    = "H:\ACTOR_DEV_ENV\sync-gdrive.log"
$ManifestFile = "H:\ACTOR_DEV_ENV\Jus_Cogens_AIPS-2025_Manifest.txt"

# Evidence files to sync and track
$EvidenceFiles = @(
    "Raport_Jus_Cogens_Macheret_Auto-Deconspirare_Final.pdf",
    "CANONICAL_JUS_COGENS_MASTER_2026.json",
    "SYSTEM_INTEGRITY_MANIFEST.json",
    "audit_log.json",
    "Jus_Cogens_AIPS-2025_Manifest.txt"
)

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    Add-Content $LogFile $line
}

Write-Log "=== SYNC START ==="

# 1. Sync evidence files to Google Drive
Write-Log "Syncing evidence files to $RemotePath ..."
foreach ($f in $EvidenceFiles) {
    $src = Join-Path $LocalDir $f
    if (Test-Path $src) {
        & $rclone copy $src "$RemotePath/" --checksum 2>&1 | ForEach-Object { Write-Log "  rclone: $_" }
        Write-Log "  Uploaded: $f"
    } else {
        Write-Log "  SKIP (not found): $f"
    }
}

# Also sync apostille-mirror folder (--ignore-errors handles duplicate objects on Drive)
Write-Log "Syncing apostille-mirror/ ..."
$ErrorActionPreference = "Continue"
& $rclone copy "$LocalDir\apostille-mirror" "$RemotePath/apostille-mirror" --checksum --ignore-errors 2>&1 | ForEach-Object {
    if ($_ -match "NOTICE|WARNING") { Write-Log "  rclone warn: $_" }
    elseif ($_ -match "ERROR") { Write-Log "  rclone error: $_" }
}
$ErrorActionPreference = "Stop"
Write-Log "apostille-mirror sync done"

# 2. Regenerate SHA-256 manifest (LF, no BOM)
Write-Log "Regenerating SHA-256 manifest ..."
$lines = @()
foreach ($f in $EvidenceFiles | Where-Object { $_ -ne "Jus_Cogens_AIPS-2025_Manifest.txt" }) {
    $path = Join-Path $LocalDir $f
    if (Test-Path $path) {
        $hash = (Get-FileHash $path -Algorithm SHA256).Hash.ToLower()
        $lines += "$hash  $f"
        Write-Log "  SHA256: $hash  $f"
    }
}
$content = $lines -join "`n"
[System.IO.File]::WriteAllText($ManifestFile, $content + "`n", [System.Text.UTF8Encoding]::new($false))
Write-Log "Manifest updated: $ManifestFile"

# Upload updated manifest
& $rclone copy $ManifestFile "$RemotePath/" --checksum 2>&1 | ForEach-Object { Write-Log "  rclone: $_" }

# 3. Commit manifest update to GitHub
Write-Log "Committing manifest to GitHub ..."
Set-Location $LocalDir
$ts = Get-Date -Format "yyyyMMddHHmmss"
git add Jus_Cogens_AIPS-2025_Manifest.txt 2>&1 | ForEach-Object { Write-Log "  git: $_" }
$status = git status --short
if ($status -match "^M|^A") {
    git commit -m "sync: update SHA-256 manifest $ts [gdrive-sync]" 2>&1 | ForEach-Object { Write-Log "  git: $_" }
    git push origin main 2>&1 | ForEach-Object { Write-Log "  git: $_" }
    Write-Log "Git commit and push: OK"
} else {
    Write-Log "No manifest changes to commit."
}

Write-Log "=== SYNC COMPLETE ==="