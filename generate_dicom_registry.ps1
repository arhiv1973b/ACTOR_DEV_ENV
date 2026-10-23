# PowerShell Script: DICOM Evidence Registry Generator
# This script identifies files in C:\A\ that lack extensions (likely raw DICOM)
# and generates a CSV file with their paths and SHA-256 hashes.

$rootPath = "C:\A"
$outputPath = "H:\ACTOR_DEV_ENV\DICOM_Evidence_Registry.csv"

Write-Host "Starting scan in $rootPath..."

# Get files without extensions, recursively
$files = Get-ChildItem -Path $rootPath -Recurse -File | Where-Object { $_.Extension -eq "" }

$registry = foreach ($file in $files) {
    Write-Host "Processing $($file.FullName)..."
    
    # Calculate SHA256
    $hash = Get-FileHash -Path $file.FullName -Algorithm SHA256
    
    [PSCustomObject]@{
        Path = $file.FullName
        SHA256 = $hash.Hash
        LastWriteTime = $file.LastWriteTime
    }
}

# Export to CSV
$registry | Export-Csv -Path $outputPath -NoTypeInformation -Encoding UTF8

Write-Host "Registry generated at $outputPath"
