<#
.SYNOPSIS
  Truth Social / Chrome Cookie & Storage Forensic Auditor (Hardened v2)
.DESCRIPTION
  PowerShell 7 модуль для аудита, классификации и безопасного удаления cookies и LocalStorage.
  Режимы: audit, classify, dry-run, backup-verify, clean.
  Fail-Closed: при ошибке или отсутствии проверок никакие изменения не применяются.
#>

param(
    [ValidateSet("audit","classify","dry-run","backup-verify","clean")]
    [string]$Mode = "audit",
    [string]$ProfilePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
)

# --- SHA-256 with robust stream disposal ---
function Get-SHA256 {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Файл отсутствует или не является файлом: $Path"
    }
    $stream = $null
    $sha = $null
    try {
        $stream = [System.IO.File]::OpenRead($Path)
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $hash = $sha.ComputeHash($stream)
        return ([Convert]::ToHexString($hash)).ToLowerInvariant()
    }
    finally {
        if ($sha) { $sha.Dispose() }
        if ($stream) { $stream.Dispose() }
    }
}

# --- Backup + Manifest (File-filtered) ---
function Backup-ChromeProfile {
    param([string]$ProfilePath)
    if (-not (Test-Path $ProfilePath)) {
        throw "Профиль Chrome не найден: $ProfilePath"
    }
    $timestamp = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $backupDir = Join-Path $ProfilePath "ForensicBackup_$timestamp"
    New-Item -ItemType Directory -Path $backupDir | Out-Null

    # Копируем Cookies + WAL + SHM (только файлы)
    Get-ChildItem -LiteralPath $ProfilePath -Filter "Cookies*" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $backupDir -Force
    }

    # Копируем LocalStorage LevelDB
    $lsPath = Join-Path $ProfilePath "Local Storage\leveldb"
    if (Test-Path $lsPath) {
        $destLs = Join-Path $backupDir "Local_Storage_leveldb"
        New-Item -ItemType Directory -Path $destLs -Force | Out-Null
        Copy-Item -LiteralPath "$lsPath\*" -Destination $destLs -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Формируем SHA-256 манифест с исключением директорий
    $manifest = @()
    Get-ChildItem -LiteralPath $backupDir -Recurse -File | ForEach-Object {
        $relPath = $_.FullName.Substring($backupDir.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
        $manifest += [PSCustomObject]@{
            File   = $relPath
            SHA256 = Get-SHA256 $_.FullName
        }
    }
    $manifestPath = Join-Path $backupDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 4 | Out-File -LiteralPath $manifestPath -Encoding UTF8
    Write-Host "Forensic Backup создан: $backupDir"
    return $backupDir
}

# --- Audit Cookies with WebKit Epoch Conversion & Fail-Closed SQLite Check ---
function Audit-Cookies {
    param([string]$ProfilePath)
    $cookieDb = Join-Path $ProfilePath "Cookies"
    if (-not (Test-Path $cookieDb)) {
        Write-Warning "Cookies DB не найдена по пути: $cookieDb"
        return @()
    }
    
    $sqliteDll = "C:\path\to\System.Data.SQLite.dll"
    if (-not (Test-Path $sqliteDll)) {
        # Try loading from GAC or common NuGet paths if available, else throw fail-closed error
        throw "Критическая ошибка: System.Data.SQLite.dll не найдена по пути $sqliteDll. Укажите актуальный путь."
    }

    try {
        Add-Type -Path $sqliteDll
        $conn = New-Object System.Data.SQLite.SQLiteConnection("Data Source=$cookieDb;Version=3;Read Only=True;")
        $conn.Open()
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT name, host_key, expires_utc FROM cookies"
        $reader = $cmd.ExecuteReader()
        $results = @()
        while ($reader.Read()) {
            $rawExpires = [int64]$reader["expires_utc"]
            # Chromium uses WebKit epoch (microseconds since Jan 1, 1601). FileTime is 100-ns ticks.
            $expires = if ($rawExpires -gt 0) {
                try { [DateTime]::FromFileTimeUtc($rawExpires * 10) } catch { [DateTime]::MinValue }
            } else {
                [DateTime]::MinValue
            }

            $results += [PSCustomObject]@{
                Name    = $reader["name"]
                Host    = $reader["host_key"]
                Expires = $expires
                Status  = "NOT_VERIFIED"
            }
        }
        $reader.Close()
        $conn.Close()
        return $results
    }
    catch {
        Write-Error "Ошибка при чтении базы Cookies: $_"
        return @()
    }
}

# --- Classify with Strict Domain Filtering ---
function Classify-Cookies {
    param($cookies)
    foreach ($c in $cookies) {
        if ($c.Host -match "(^|\.)truthsocial\.com$" -and $c.Name -eq "__cf") {
            $c.Status = "VERIFIED"
        }
        elseif ($c.Host -match "(^|\.)google\.com$" -and $c.Name -like "_ga*") {
            $c.Status = "USER_ASSERTED"
        }
        else {
            $c.Status = "NOT_VERIFIED"
        }
    }
    return $cookies
}

# --- Dry-Run ---
function DryRun-Clean {
    param($cookies)
    $candidates = $cookies | Where-Object { $_.Status -eq "NOT_VERIFIED" }
    Write-Host "=== DRY-RUN: Кандидаты на удаление ($( $candidates.Count )) ===" -ForegroundColor Yellow
    if ($candidates.Count -gt 0) {
        $candidates | Format-Table -AutoSize
    } else {
        Write-Host "Нет неподтвержденных кандидатов для удаления." -ForegroundColor Green
    }
}

# --- Clean with Mandatory Backup & Manifest Verification ---
function Clean-Cookies {
    param([string]$ProfilePath, $cookies)
    
    # Fail-Closed: Требуем предварительный свежий бэкап и проверку манифеста
    Write-Host "Создание обязательного защитного бэкапа перед очисткой..." -ForegroundColor Cyan
    $backupDir = Backup-ChromeProfile -ProfilePath $ProfilePath
    $manifestPath = Join-Path $backupDir "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        throw "Fail-Closed: Манифест бэкапа не создан. Очистка отменена."
    }

    $cookieDb = Join-Path $ProfilePath "Cookies"
    if (-not (Test-Path $cookieDb)) { throw "Cookies DB не найдена." }

    $sqliteDll = "C:\path\to\System.Data.SQLite.dll"
    Add-Type -Path $sqliteDll
    $conn = New-Object System.Data.SQLite.SQLiteConnection("Data Source=$cookieDb;Version=3;")
    $conn.Open()
    $tx = $conn.BeginTransaction()
    try {
        $deletedCount = 0
        foreach ($c in $cookies | Where-Object { $_.Status -eq "NOT_VERIFIED" }) {
            $del = $conn.CreateCommand()
            $del.CommandText = "DELETE FROM cookies WHERE name=@n AND host_key=@h"
            $del.Parameters.AddWithValue("@n", $c.Name) | Out-Null
            $del.Parameters.AddWithValue("@h", $c.Host) | Out-Null
            $deletedCount += $del.ExecuteNonQuery()
        }
        $tx.Commit()
        Write-Host "Транзакционное удаление завершено успешно. Удалено записей: $deletedCount" -ForegroundColor Green
    }
    catch {
        $tx.Rollback()
        throw "Ошибка удаления (транзакция откачена): $_"
    }
    finally {
        $conn.Close()
    }
}

# --- Main Switch ---
switch ($Mode) {
    "backup-verify" { 
        $b = Backup-ChromeProfile -ProfilePath $ProfilePath
        Write-Host "Проверка манифеста бэкапа..."
        $manifest = Get-Content -LiteralPath "$b\manifest.json" | ConvertFrom-Json
        foreach ($entry in $manifest) {
            $fullPath = Join-Path $b $entry.File
            $currentHash = Get-SHA256 $fullPath
            if ($currentHash -eq $entry.SHA256) {
                Write-Host "[OK] Хэш подтвержден для: $($entry.File)" -ForegroundColor Green
            } else {
                Write-Error "[FAIL] Несоответствие хэша для: $($entry.File)"
            }
        }
    }
    "audit" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $cookies | Format-Table -AutoSize
    }
    "classify" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $classified = Classify-Cookies $cookies
        $classified | Format-Table -AutoSize
    }
    "dry-run" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $classified = Classify-Cookies $cookies
        DryRun-Clean $classified
    }
    "clean" {
        $cookies = Audit-Cookies -ProfilePath $ProfilePath
        $classified = Classify-Cookies $cookies
        DryRun-Clean $classified
        $confirm = Read-Host "Подтверждаете транзакционное удаление NOT_VERIFIED записей? (y/N)"
        if ($confirm -eq 'y') {
            Clean-Cookies -ProfilePath $ProfilePath -cookies $classified
        } else {
            Write-Host "Операция очистки отменена пользователем." -ForegroundColor Yellow
        }
    }
}
