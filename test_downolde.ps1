$files = Get-ChildItem -Path "F:\Мой диск\Downolde" -File -ErrorAction SilentlyContinue
$target = @($files | Where-Object { $_.Extension -match '^\.(exe|msi|iso|zip)$' })
Write-Host "Found installers: $($target.Count)"
foreach ($f in $target) {
    Write-Host "Removing: $($f.Name)"
    Remove-Item -LiteralPath $f.FullName -Force -ErrorAction SilentlyContinue
}
