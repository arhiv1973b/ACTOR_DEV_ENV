<#
.SYNOPSIS
    Remote Drive Metadata & SHA-256 Scanner for Jus Cogens Audit
    Scans F:\Мой диск without copying files, generating MASTER_DOSSIER manifests.
#>

param(
    [string]$SourcePath = "F:\Мой диск",
    [string]$ManifestOutput = "MASTER_DOSSIER\remote_drive_manifest.json",
    [string]$TargetIdnp = "2000001159655",
    [string[]]$TargetVariants = @("MACERET", "MACHERET", "МАЧЕРЕТ")
)

Write-Host "[*] Scanning remote path: $SourcePath (Metadata-only mode, no file copying)" -ForegroundColor Cyan

if (!(Test-Path $SourcePath)) {
    Write-Host "[!] Warning: Source path $SourcePath not found. Running in simulation/fallback mode." -ForegroundColor Yellow
}

$files = @()
if (Test-Path $SourcePath) {
    $files = Get-ChildItem -Path $SourcePath -Recurse -File -ErrorAction SilentlyContinue
}

$manifestEntries = @()

foreach ($file in $files) {
    $filePath = $file.FullName
    $fileName = $file.Name
    $fileSize = $file.Length
    $lastWrite = $file.LastWriteTime.ToString("o")

    # Compute SHA-256 hash without loading entire file into memory if possible, or via standard .NET HashAlgorithm
    $hash = ""
    try {
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $stream = [System.IO.File]::Open($filePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
        $hashBytes = $sha256.ComputeHash($stream)
        $stream.Close()
        $hash = [BitConverter]::ToString($hashBytes) -replace '-'
    } catch {
        $hash = "HASH_ERROR_OR_LOCKED"
    }

    # Lightweight metadata check on filename and path
    $idnpMatched = $fileName -match $TargetIdnp -or $filePath -match $TargetIdnp
    $matchedVariants = @()
    foreach ($v in $TargetVariants) {
        if ($fileName -like "*$v*" -or $filePath -like "*$v*") {
            $matchedVariants += $v
        }
    }

    $entry = [PSCustomObject]@{
        FileName         = $fileName
        FullPath         = $filePath
        FileSize         = $fileSize
        LastModified     = $lastWrite
        Sha256           = $hash
        IdnpMatch        = $idnpMatched
        MatchedVariants  = $matchedVariants
        JusCogensStatus  = if ($idnpMatched -or $matchedVariants.Count -gt 0) { "VERIFIED_REFERENCE" } else { "STANDARD" }
    }

    $manifestEntries += $entry
    Write-Host "[+] Scanned: $fileName | SHA256: $($hash.Substring(0, 12))..." -ForegroundColor Green

    # Ensure output directory exists and save incrementally
    $outputDir = Split-Path $ManifestOutput -Parent
    if ($outputDir -and !(Test-Path $outputDir)) {
        New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
    }
    $manifestEntries | ConvertTo-Json -Depth 5 | Set-Content -Path $ManifestOutput -Encoding UTF8
}

Write-Host "[*] Scan complete. Metadata manifest saved to $ManifestOutput ($( $manifestEntries.Count ) files indexed)." -ForegroundColor Cyan
