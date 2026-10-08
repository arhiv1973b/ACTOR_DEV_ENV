# scan_external_drive.ps1
param(
    [string]$SourcePath = "F:\Мой диск",
    [string]$ManifestOutput = "MASTER_DOSSIER\external_drive_manifest.json",
    [string]$TargetIdnp = "2000001159655",
    [string[]]$TargetVariants = @("MACERET", "MACHERET", "МАЧЕРЕТ")
)

if (-not (Test-Path $SourcePath)) {
    Write-Warning "Source path '$SourcePath' is not accessible. Using simulation mode or checking available drives."
    # Fallback to current directory or prompt
}

$ManifestDir = [System.IO.Path]::GetDirectoryName($ManifestOutput)
if (-not (Test-Path $ManifestDir)) {
    New-Item -ItemType Directory -Path $ManifestDir -Force | Out-Null
}

Write-Host "[*] Scanning metadata and computing SHA-256 hashes from $SourcePath (No file duplication)..."

$Manifest = @()
$Files = Get-ChildItem -Path $SourcePath -Recurse -File -ErrorAction SilentlyContinue

foreach ($File in $Files) {
    try {
        # Compute SHA-256 hash without loading entire file into memory if possible, or using Get-FileHash
        $HashObj = Get-FileHash -Path $File.FullName -Algorithm SHA256 -ErrorAction Stop
        $Sha256 = $HashObj.Hash

        $MatchIdnp = $false
        $MatchedVariants = @()

        # If file is text or small enough, or check filename
        if ($File.Name -match "$TargetIdnp|MACERET|MACHERET|МАЧЕРЕТ") {
            $MatchIdnp = $true
        }

        # Check filename for variants
        foreach ($v in $TargetVariants) {
            if ($File.Name -like "*$v*") {
                $MatchedVariants += $v
            }
        }

        $Record = @{
            FileName       = $File.Name
            FullPath       = $File.FullName
            Size           = $File.Length
            LastWriteTime  = $File.LastWriteTime.ToString("o")
            Sha256         = $Sha256
            IdnpMatch      = $MatchIdnp
            MatchedVariants = $MatchedVariants
        }

        $Manifest += $Record
        Write-Host "[OK] Indexed metadata for: $($File.Name) [SHA256: $($Sha256.Substring(0, 16))...]"
    }
    catch {
        Write-Warning "Failed to process file: $($File.FullName). Error: $_"
    }
}

$Manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $ManifestOutput -Encoding UTF8
Write-Host "[SUCCESS] Metadata manifest generated at $ManifestOutput without duplicating files."
