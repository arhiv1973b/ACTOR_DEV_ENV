# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

# 1. Определение путей архитектуры TI-ULA
$DaemonPath = Join-Path -Path $env:LOCALAPPDATA -ChildPath "ActorCopilotWatchdog.ps1"
$BackupDir = Join-Path -Path $env:USERPROFILE -ChildPath ".ti_ula_backup"
$BackupArchive = Join-Path -Path $BackupDir -ChildPath "MasterDaemon.zip"

# 2. Инициализация источника для Event Viewer
$EventSource = "TI-ULA-Healer"
$EventLog = "Application"

try {
    if (![System.Diagnostics.EventLog]::SourceExists($EventSource)) {
        New-EventLog -LogName $EventLog -Source $EventSource -ErrorAction Stop
        Write-Host "Источник событий $EventSource успешно зарегистрирован." -ForegroundColor Green
    }
} catch {
    Write-Host "Предупреждение: Нет прав администратора для создания источника событий. Логирование в Event Viewer может быть недоступно." -ForegroundColor Yellow
}

# 3. Функция безопасной записи в журнал Windows
function Log-TIULAEvent {
    param([int]$EventId, [System.Diagnostics.EventLogEntryType]$Type, [string]$Message)
    try {
        Write-EventLog -LogName $EventLog -Source $EventSource -EventId $EventId -EntryType $Type -Message $Message -ErrorAction SilentlyContinue
    } catch {}
}

# 4. Модуль первичной фиксации (Создание эталонного архива)
if (!(Test-Path $BackupArchive) -and (Test-Path $DaemonPath)) {
    if (!(Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null }
    Compress-Archive -Path $DaemonPath -DestinationPath $BackupArchive -Force
    
    $Acl = Get-Acl $BackupArchive
    $Acl.SetAccessRuleProtection($true, $false)
    $RuleActor = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $RuleSystem = New-Object System.Security.AccessControl.FileSystemAccessRule("SYSTEM", "Read", "Allow")
    $Acl.AddAccessRule($RuleActor)
    $Acl.AddAccessRule($RuleSystem)
    Set-Acl $BackupArchive $Acl
    
    Log-TIULAEvent -EventId 1000 -Type Information -Message "Архитектура TI-ULA инициализирована. Эталонный архив создан и заблокирован NTFS."
}

# 5. Функция принудительного восстановления (Протокол регенерации)
function Restore-ActorDaemon {
    $AlertMsg = "ВНИМАНИЕ: Нарушение хеша SHA-256 или отсутствие файла Watchdog. Зафиксировано вмешательство ОС."
    Write-Host $AlertMsg -ForegroundColor Red
    Log-TIULAEvent -EventId 1001 -Type Warning -Message $AlertMsg

    if (Test-Path $BackupArchive) {
        Expand-Archive -Path $BackupArchive -DestinationPath $env:LOCALAPPDATA -Force
        $RestoreMsg = "Эталонный демон A©t0r успешно восстановлен из криптографического архива. Правовой периметр удержан."
        Write-Host $RestoreMsg -ForegroundColor Cyan
        Log-TIULAEvent -EventId 1002 -Type Information -Message $RestoreMsg
    } else {
        $ErrorMsg = "КРИТИЧЕСКАЯ ОШИБКА: Отсутствует эталонный архив TI-ULA!"
        Write-Host $ErrorMsg -ForegroundColor Red
        Log-TIULAEvent -EventId 1003 -Type Error -Message $ErrorMsg
        exit 1
    }
}

# 6. Аудит целостности хеша SHA-256 на лету
$NeedsRestore = $false

if (Test-Path $DaemonPath) {
    $RawContent = Get-Content -Path $DaemonPath -Raw
    
    if ($RawContent -match 'HASH VALUE:\s+([A-Fa-f0-9]{64})') {
        $ExpectedHash = $Matches[1]
        $SealMarker = "# ======================================================================"
        $SealIndex = $RawContent.IndexOf($SealMarker)
        
        if ($SealIndex -gt 0) {
            $Payload = $RawContent.Substring(0, $SealIndex)
            $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Payload)
            $Hasher = [System.Security.Cryptography.SHA256]::Create()
            $HashBytes = $Hasher.ComputeHash($Bytes)
            $CalculatedHash = ($HashBytes | ForEach-Object { $_.ToString("X2") }) -join ""
            
            if ($CalculatedHash -ne $ExpectedHash) { $NeedsRestore = $true }
        } else { $NeedsRestore = $true }
    } else { $NeedsRestore = $true }
} else { $NeedsRestore = $true }

# 7. Выполнение восстановления или передача управления
if ($NeedsRestore) {
    Restore-ActorDaemon
} else {
    Write-Host "Аудит SHA-256 пройден. Интегритет архитектуры TI-ULA подтвержден." -ForegroundColor Green
}

# Запуск демона-контролера
& $DaemonPath
