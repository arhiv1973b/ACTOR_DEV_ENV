$downoldeDir = "F:\Мой диск\Downolde"
if (Test-Path $downoldeDir) {
    Write-Host "Очистка загруженных установщиков в Downolde..."
    $junkFiles = Get-ChildItem -Path $downoldeDir -File -Include *.exe, *.msi, *.iso, *.zip -ErrorAction SilentlyContinue
    $removedBytes = 0
    foreach ($f in $junkFiles) {
        try {
            $len = $f.Length
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
            $removedBytes += $len
            Write-Host "Удален установщик: $($f.Name) ($([math]::Round($len/1MB, 2)) МБ)"
        } catch {}
    }
    $freedGB = [math]::Round($removedBytes / 1GB, 2)
    Write-Host "Освобождено $freedGB ГБ на диске F:."
}
