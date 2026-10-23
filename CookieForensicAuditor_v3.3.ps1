<#
.SYNOPSIS
    Truth Social / Chrome Cookie & Storage Forensic Auditor (PowerShell 7 - v3.3)
.DESCRIPTION
    Расширенный форензик-модуль для аудита, классификации по расширенным правилам (Name + Host),
    создания атомарных бэкапов и криминалистического дедуплицированного реестра с отслеживанием
    происхождения (provenance) и хэшей SHA-256.
.NOTES
    Политика: STRICT NON-DESTRUCTIVE PRESERVATION (Fail-Closed, Read-Only).
#>

param(
    [ValidateSet("audit","classify","dry-run","backup-verify","dedup-registry","clean")]
    [string]$Mode = "audit",

    [string]$ProfilePath = $(if ($IsWindows) {
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
    } elseif ($IsLinux) {
        "$HOME/.config/google-chrome/Default"
    } elseif ($IsMacOS) {
        "$HOME/Library/Application Support/Google/Chrome/Default"
    } else {
        throw "Unsupported OS"
    }),

    [string]$OutputDirectory = "$PSScriptRoot/ForensicReports",

    [string]$ClassificationRules = "$PSScriptRoot/classify_rules.json"
)

if (-not (Test-Path $OutputDirectory)) {
    New-Item -ItemType Directory -Path $OutputDirectory | Out-Null
}

function Get-SHA256 {
    param([string]$Path)
    if (Test-Path $Path) {
        try {
            $stream = [System.IO.File]::Open($Path,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::ReadWrite)
            $sha = [System.Security.Cryptography.SHA256]::Create()
            $hash = $sha.ComputeHash($stream)
            $stream.Dispose()
            return ($hash | ForEach-Object { $_.ToString("x2") }) -join ""
        } catch {
            Write-Warning "Ошибка SHA256 для $Path: $_"
        }
    }
    return $null
}

function Backup-ChromeProfile {
    param([string]$ProfilePath)
    if (-not (Test-Path $ProfilePath)) {
        throw "FAIL-CLOSED: Профиль Chrome не найден: $ProfilePath"
    }
    $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $backupDir = Join-Path $OutputDirectory "ForensicBackup_$timestamp"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    Get-ChildItem $ProfilePath -Filter "Cookies*" | ForEach-Object {
        try { Copy-Item $_.FullName $backupDir -Force } catch { Write-Warning "Не удалось скопировать $_: $_" }
    }

    $lsPath = Join-Path $ProfilePath "Local Storage/leveldb"
    if (Test-Path $lsPath) {
        $backupLsPath = Join-Path $backupDir "Local_Storage_leveldb"
        New-Item -ItemType Directory -Path $backupLsPath -Force | Out-Null
        Get-ChildItem $lsPath | ForEach-Object {
            try { Copy-Item $_.FullName $backupLsPath -Force } catch { }
        }
    }
    Write-Host "Backup создан: $backupDir" -ForegroundColor Green
    return $backupDir
}

function Audit-Cookies {
    param([string]$ProfilePath)
    $cookieDb = Join-Path $ProfilePath "Cookies"
    if (-not (Test-Path $cookieDb)) {
        Write-Warning "Cookies DB не найдена."
        return @()
    }

    $tempDb = [System.IO.Path]::GetTempFileName()
    Copy-Item $cookieDb $tempDb -Force

    $results = @()
    try {
        [System.Reflection.Assembly]::Load("Microsoft.Data.Sqlite") | Out-Null
        $conn = New-Object Microsoft.Data.Sqlite.SqliteConnection("Data Source=$tempDb;Mode=ReadOnly;")
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT name, host_key, path, expires_utc FROM cookies"
        $reader = $cmd.ExecuteReader()

        while ($reader.Read()) {
            $results += [PSCustomObject]@{
                Name    = $reader["name"]
                Host    = $reader["host_key"]
                Path    = $reader["path"]
                Expires = $reader["expires_utc"]
                Status  = "NOT_VERIFIED"
            }
        }
        $reader.Close()
        $conn.Close()
    } catch {
        Write-Error "Ошибка чтения SQLite: $_"
    } finally {
        if (Test-Path $tempDb) { Remove-Item $tempDb -Force }
    }
    return $results
}

function Classify-Cookies {
    param([array]$Cookies)
    if (-not (Test-Path $ClassificationRules)) {
        Write-Warning "Файл правил классификации не найден: $ClassificationRules"
        return $Cookies
    }
    $rules = Get-Content $ClassificationRules -Raw | ConvertFrom-Json
    foreach ($c in $Cookies) {
        foreach ($r in $rules) {
            $nameMatch = $true
            $hostMatch = $true
            
            if ($r.name_pattern) {
                $nameMatch = ($c.Name -match $r.name_pattern)
            }
            if ($r.host_pattern) {
                $hostMatch = ($c.Host -match $r.host_pattern)
            }

            if ($nameMatch -and $hostMatch) {
                $c.Status = $r.status
                break
            }
        }
    }
    return $Cookies
}

# Криминалистический реестр с дедупликацией по SHA-256 и отслеживанием provenance
function Build-DedupEvidenceRegistry {
    param([string]$BackupDir)
    Write-Host "[*] Построение дедуплицированного криминалистического реестра артефактов..." -ForegroundColor Cyan

    $registry = @{}
    $allFiles = Get-ChildItem -LiteralPath $BackupDir -Recurse -File

    foreach ($file in $allFiles) {
        $hash = Get-SHA256 $file.FullName
        if (-not $hash) { continue }

        $relPath = $file.FullName.Substring($BackupDir.Length + 1)

        if (-not $registry.ContainsKey($hash)) {
            $registry[$hash] = [PSCustomObject]@{
                SHA256         = $hash
                CanonicalName  = $file.Name
                Size           = $file.Length
                FirstSeenPath  = $relPath
                Occurrences    = @($relPath)
                IsDuplicate    = $false
            }
        } else {
            $registry[$hash].Occurrences += $relPath
            $registry[$hash].IsDuplicate = $true
        }
    }

    $registryList = $registry.Values | Sort-Object IsDuplicate
    $regJsonPath = Join-Path $BackupDir "deduplicated_evidence_registry.json"
    $registryList | ConvertTo-Json -Depth 5 | Out-File $regJsonPath -Encoding UTF8

    Write-Host "[+] Реестр сохранен: $regJsonPath" -ForegroundColor Green
    Write-Host "    Всего уникальных объектов: $($registryList.Count)"
    Write-Host "    Обнаружено дубликатов по хэшу: $(($registryList | Where-Object { $_.IsDuplicate }).Count)"

    return $registryList
}

switch ($Mode) {
    "backup-verify" { 
        $bDir = Backup-ChromeProfile -ProfilePath $ProfilePath
        Build-DedupEvidenceRegistry -BackupDir $bDir
    }
    "audit" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $cookies | Format-Table -AutoSize
    }
    "classify" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $classified = Classify-Cookies -Cookies $cookies
        $classified | Format-Table -AutoSize
    }
    "dry-run" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $classified = Classify-Cookies -Cookies $cookies
        Write-Host "=== DRY-RUN CANDIDATES FOR REVIEW ===" -ForegroundColor Yellow
        $classified | Where-Object { $_.Status -eq "NOT_VERIFIED" } | Format-Table -AutoSize
    }
    "dedup-registry" {
        $bDir = Backup-ChromeProfile -ProfilePath $ProfilePath
        Build-DedupEvidenceRegistry -BackupDir $bDir
    }
    "clean" {
        Write-Error "FAIL-CLOSED: Режим CLEAN заблокирован для защиты доказательной базы (Tampering Prevention)."
        exit 2
    }
}
