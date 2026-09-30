param(
    [string]$SearchRoot = "F:\Мой диск",
    [int64]$TargetFreedBytes = 150 * 1024 * 1024
)

function Get-FileHashSHA256 {
    param([string]$Path)
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hashBytes = $sha256.ComputeHash($stream)
        $stream.Close()
        return ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
    } catch { return $null }
}

Write-Host "Сканирование файлов < 20 МБ для освобождения кэша..."
$maxSize = 20 * 1024 * 1024
$files = Get-ChildItem -Path $SearchRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 0 -and $_.Length -lt $maxSize -and $_.FullName -notmatch '\.git' }

$groups = $files | Group-Object Length
$freedBytes = 0

foreach ($group in $groups) {
    if ($group.Count -gt 1) {
        $hashTable = @{}
        foreach ($f in $group.Group) {
            $digest = Get-FileHashSHA256 $f.FullName
            if ($digest) {
                if (-not $hashTable.ContainsKey($digest)) { $hashTable[$digest] = @() }
                $hashTable[$digest] += $f.FullName
            }
        }

        foreach ($kvp in $hashTable.GetEnumerator()) {
            $paths = $kvp.Value
            if ($paths.Count -gt 1) {
                $original = $paths | Where-Object { $_ -match "CASE-MACHERET-EVIDENCE-FINAL" -or $_ -match "A©torVault" } | Select-Object -First 1
                if (-not $original) { $original = $paths[0] }
                
                $duplicates = $paths | Where-Object { $_ -ne $original }
                foreach ($dup in $duplicates) {
                    if ($freedBytes -ge $TargetFreedBytes) { break }
                    try {
                        $len = (Get-Item -LiteralPath $dup).Length
                        Remove-Item -LiteralPath $dup -Force -ErrorAction Stop
                        $freedBytes += $len
                        Write-Host "Удален дубликат: $dup ($len байт)"
                    } catch {}
                }
            }
        }
    }
    if ($freedBytes -ge $TargetFreedBytes) { break }
}

$freedMB = [math]::Round($freedBytes / 1MB, 2)
Write-Host "Освобождено $freedMB МБ. Лимит достигнут. Запуск миграции LFS..."

if (Test-Path "H:\ACTOR_DEV_ENV\migrate_lfs.ps1") {
    & "H:\ACTOR_DEV_ENV\migrate_lfs.ps1"
}
