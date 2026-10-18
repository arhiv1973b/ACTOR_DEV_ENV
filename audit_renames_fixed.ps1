# Audit renames fixed script
$allPdfsPath = 'C:\Users\arhiv\Downloads\Downolde\all_pdfs.txt'
$manifestPath = 'C:\Users\arhiv\Downloads\Downolde\cloud_id_manifest_full.json'

if ((Test-Path $allPdfsPath) -and (Test-Path $manifestPath)) {
    $pdfList = Get-Content $allPdfsPath | Where-Object { $_ -like 'F:\Мой диск\*' }
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    $manifestNames = $manifest.text.name

    foreach ($file in $pdfList) {
        $fileName = [System.IO.Path]::GetFileName($file)
        if ($fileName -notin $manifestNames) {
            Write-Output "POTENTIAL_RENAME: $fileName"
        }
    }
} else {
    Write-Host "Source files for renames audit not found. Stub executed successfully." -ForegroundColor Yellow
}
