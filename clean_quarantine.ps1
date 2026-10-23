$quarantineDir = "F:\Мой диск\Quarantine_Conflicting_Copies"
if (Test-Path $quarantineDir) {
    Write-Host "Очистка папки конфликтных копий Google Drive для освобождения кэша..."
    $files = Get-ChildItem -Path $quarantineDir -Recurse -File -ErrorAction SilentlyContinue
    $removedBytes = 0
    foreach ($f in $files) {
        try {
            $len = $f.Length
            Remove-Item -LiteralPath $f.FullName -Force -ErrorAction Stop
            $removedBytes += $len
            Write-Host "Удалена конфликтная копия: $($f.Name)"
        } catch {}
    }
    $freedMB = [math]::Round($removedBytes / 1MB, 2)
    Write-Host "Освобождено $freedMB МБ на диске F:."
}

if (Test-Path "H:\ACTOR_DEV_ENV\migrate_lfs.ps1") {
    Write-Host "Запуск миграции LFS..."
    & "H:\ACTOR_DEV_ENV\migrate_lfs.ps1"
}
