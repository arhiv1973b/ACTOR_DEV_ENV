param(
    [Parameter(Mandatory=$false)]
    [string]$TargetDir = "F:\Мой диск"
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

# 1. Мусор: *.exe, *.msi
$junkFiles = Get-ChildItem -Path $TargetDir -Recurse -File -Include *.exe, *.msi -ErrorAction SilentlyContinue
$junkSizeGB = [math]::Round(($junkFiles | Measure-Object Length -Sum).Sum / 1GB, 2)
Write-Host "Мусорных файлов найдено: $($junkFiles.Count). Общий объем: $junkSizeGB ГБ"

# 2. Защищенные форматы
$protectedExt = @("*.pdf","*.doc","*.docx","*.xls","*.xlsx","*.rtf","*.csv",
                  "*.jpg","*.jpeg","*.png","*.tiff","*.bmp","*.heic",
                  "*.mp3","*.wav","*.m4a","*.flac",
                  "*.mp4","*.mkv","*.avi","*.mov")

$files = Get-ChildItem -Path $TargetDir -Recurse -File -Include $protectedExt -ErrorAction SilentlyContinue

# Группировка по размеру
$groups = $files | Group-Object Length

$hashTable = @{}
foreach ($group in $groups) {
    if ($group.Count -gt 1) {
        foreach ($f in $group.Group) {
            $digest = Get-FileHashSHA256 $f.FullName
            if ($digest) {
                if (-not $hashTable.ContainsKey($digest)) { $hashTable[$digest] = @() }
                $hashTable[$digest] += $f.FullName
            }
        }
    }
}

$dupCount = 0
$dupSize = 0
foreach ($kvp in $hashTable.GetEnumerator()) {
    $paths = $kvp.Value
    if ($paths.Count -gt 1) {
        $original = $paths | Where-Object { $_ -match "CASE-MACHERET-EVIDENCE-FINAL" -or $_ -match "A©torVault" }
        if (-not $original) { $original = $paths[0] }
        $duplicates = $paths | Where-Object { $_ -ne $original }
        $dupCount += $duplicates.Count
        $dupSize += ($duplicates | Get-Item | Measure-Object Length -Sum).Sum
    }
}

$dupSizeGB = [math]::Round($dupSize / 1GB, 2)
Write-Host "Найдено дубликатов доказательств: $dupCount шт. Потенциально освободится: $dupSizeGB ГБ при замене на HardLinks"
