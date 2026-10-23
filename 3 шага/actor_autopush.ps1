# ============================================================
#  A©tor AutoPush — CASE-MACHERET-1997-2026
#  Watchdog + Daily Counter Update → GitHub Pages
#  Версия: 1.0 | 20.04.2026
# ============================================================

# ── КОНФИГУРАЦИЯ ────────────────────────────────────────────
$REPO_PATH      = "C:\Users\arhiv\apostille-mirror-work"
$COUNTER_FILE   = "jus-cogens-proof-macheret.html"
$LOG_FILE       = "C:\Users\arhiv\scripts\actor_autopush.log"
$GIT_EMAIL      = "arhiv1973b@users.noreply.github.com"
$GIT_NAME       = "arhiv1973b"

# Дата отсчёта — вычислена из точки 8169 суток на 20.04.2026
$START_DATE     = (Get-Date "2026-04-20").AddDays(-8169)

# Папка Google Drive для наблюдения (изменить если нужно)
$DRIVE_WATCH_SUBPATH = "apostille-mirror"
# ── КОНЕЦ КОНФИГУРАЦИИ ──────────────────────────────────────

# ── ФУНКЦИИ ─────────────────────────────────────────────────
function Write-Log {
    param([string]$msg, [string]$level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts][$level] $msg"
    Add-Content -Path $LOG_FILE -Value $line -Encoding UTF8
    Write-Host $line
}

function Get-GDrivePath {
    # Попытка 1: через Get-PSDrive
    $drv = Get-PSDrive -PSProvider FileSystem -ErrorAction SilentlyContinue |
           Where-Object { $_.DisplayRoot -like "*Google*" } |
           Select-Object -First 1
    if ($drv) { return "$($drv.Name):\" }

    # Попытка 2: перебор букв
    foreach ($letter in @('G','H','I','J','K')) {
        $path = "${letter}:\My Drive"
        if (Test-Path $path) { return "${letter}:\" }
    }
    return $null
}

function Get-CurrentDays {
    return [math]::Floor(((Get-Date) - $START_DATE).TotalDays)
}

function Update-DaysCounter {
    param([string]$filePath)

    if (-not (Test-Path $filePath)) {
        Write-Log "Файл не найден: $filePath" "WARN"
        return $false
    }

    $days     = Get-CurrentDays
    $content  = Get-Content $filePath -Raw -Encoding UTF8
    $changed  = $false

    # Паттерны: 8169, 8,169, 8 169 → текущее значение
    $patterns = @(
        @{ pattern = '\b(\d{4,5})\b(?=\s*суток)';    space = '' },
        @{ pattern = '\b(\d{1,2}),(\d{3})\b(?=\s*(days|суток|zile|jours))'; space = ',' },
        @{ pattern = '\b(\d{1,2})\s(\d{3})\b(?=\s*(суток|zile|jours))';    space = ' ' }
    )

    # Простая замена: ищем все числа 8100-8999 рядом со словами суток/days/zile/jours
    $newContent = $content `
        -replace '(?<!\d)(8\d{3})(?=\s*(суток|days|zile|jours))', "$days" `
        -replace '(?<!\d)(8[,\s]\d{3})(?=\s*(суток|days|zile|jours))', {
            $fmt = if ($_.Value -match ',') { "{0:N0}" -f $days } else { ($days.ToString() -replace '(\d)(\d{3})$','$1 $2') }
            $fmt
        }

    # Форматированные варианты
    $daysPlain  = "$days"
    $daysComma  = "{0:N0}" -f $days   # 8,169
    $daysSpace  = $days.ToString() -replace '(\d)(\d{3})$','$1 $2'  # 8 169

    # Найти и заменить все существующие значения счётчика
    $newContent = $content
    foreach ($old in @(8158..8200)) {
        $oldComma = "{0:N0}" -f $old
        $oldSpace = $old.ToString() -replace '(\d)(\d{3})$','$1 $2'
        if ($newContent -match [regex]::Escape($old.ToString()) -or
            $newContent -match [regex]::Escape($oldComma) -or
            $newContent -match [regex]::Escape($oldSpace)) {
            $newContent = $newContent `
                -replace [regex]::Escape($oldComma),  $daysComma `
                -replace [regex]::Escape($oldSpace),  $daysSpace `
                -replace [regex]::Escape($old.ToString()), $daysPlain
            $changed = $true
        }
    }

    if ($changed) {
        Set-Content $filePath $newContent -Encoding UTF8
        Write-Log "Счётчик обновлён: $days суток → $filePath"
        return $true
    }
    Write-Log "Счётчик актуален ($days), изменений нет: $filePath"
    return $false
}

function Invoke-GitPush {
    param([string]$repoPath, [string]$message)

    Push-Location $repoPath
    try {
        & git config user.email $GIT_EMAIL
        & git config user.name  $GIT_NAME
        & git add -A
        $status = & git status --porcelain
        if (-not $status) {
            Write-Log "Нет изменений для коммита."
            return
        }
        & git commit -m $message
        & git push origin main
        Write-Log "Push выполнен: $message"
    }
    catch {
        Write-Log "Ошибка git: $_" "ERROR"
    }
    finally {
        Pop-Location
    }
}

function Sync-DriveToRepo {
    param([string]$driveFolder, [string]$repoPath)

    if (-not (Test-Path $driveFolder)) {
        Write-Log "Папка Drive не найдена: $driveFolder" "WARN"
        return
    }

    $htmlFiles = Get-ChildItem -Path $driveFolder -Filter "*.html" -Recurse
    $copied = 0

    foreach ($file in $htmlFiles) {
        $dest = Join-Path $repoPath $file.Name
        if (-not (Test-Path $dest) -or
            (Get-FileHash $file.FullName).Hash -ne (Get-FileHash $dest).Hash) {
            Copy-Item $file.FullName $dest -Force
            Write-Log "Скопирован: $($file.Name)"
            $copied++
        }
    }

    if ($copied -gt 0) {
        Write-Log "Синхронизировано файлов: $copied"
    }
    return $copied
}

# ── ЗАПУСК ──────────────────────────────────────────────────
Write-Log "=== A©tor AutoPush запущен ==="

# Создать папку для логов если нет
$logDir = Split-Path $LOG_FILE
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

# Определить Google Drive
$gdriveLetter = Get-GDrivePath
if ($gdriveLetter) {
    Write-Log "Google Drive обнаружен: $gdriveLetter"
    $DRIVE_WATCH_PATH = Join-Path $gdriveLetter "My Drive\$DRIVE_WATCH_SUBPATH"
} else {
    Write-Log "Google Drive не обнаружен — синхронизация с Drive отключена" "WARN"
    $DRIVE_WATCH_PATH = $null
}

# Запомнить время последнего обновления счётчика
$lastCounterUpdate = (Get-Date).Date.AddDays(-1)

# ── WATCHDOG: FileSystemWatcher ──────────────────────────────
if ($DRIVE_WATCH_PATH -and (Test-Path $DRIVE_WATCH_PATH)) {
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path   = $DRIVE_WATCH_PATH
    $watcher.Filter = "*.html"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents   = $true
    $watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor
                            [System.IO.NotifyFilters]::FileName

    $action = {
        $path = $Event.SourceEventArgs.FullPath
        $name = $Event.SourceEventArgs.Name
        Write-Log "Изменение обнаружено: $name"

        Start-Sleep -Seconds 3  # дать файлу записаться

        # Скопировать изменённый файл в репозиторий
        $dest = Join-Path $using:REPO_PATH (Split-Path $name -Leaf)
        Copy-Item $path $dest -Force
        Write-Log "Скопирован в репозиторий: $name"

        # Обновить счётчик суток
        Update-DaysCounter -filePath $dest

        # Push
        $days = Get-CurrentDays
        Invoke-GitPush -repoPath $using:REPO_PATH `
                       -message "A©tor: auto-sync from Drive — $name [$days d]"
    }

    Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
    Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
    Write-Log "Watchdog активен: $DRIVE_WATCH_PATH"
} else {
    Write-Log "Watchdog отключён (папка Drive недоступна)" "WARN"
}

# ── ОСНОВНОЙ ЦИКЛ ───────────────────────────────────────────
Write-Log "Основной цикл запущен. Ctrl+C для остановки."

while ($true) {
    $now  = Get-Date
    $today = $now.Date

    # Ежедневное обновление счётчика (один раз в сутки)
    if ($today -gt $lastCounterUpdate) {
        Write-Log "Ежедневное обновление счётчика суток..."

        $files = @(
            (Join-Path $REPO_PATH $COUNTER_FILE),
            (Join-Path $REPO_PATH "artifact\$COUNTER_FILE")
        )

        $anyChanged = $false
        foreach ($f in $files) {
            if (Update-DaysCounter -filePath $f) { $anyChanged = $true }
        }

        # Синхронизация с Drive если доступна
        if ($DRIVE_WATCH_PATH -and (Test-Path $DRIVE_WATCH_PATH)) {
            $synced = Sync-DriveToRepo -driveFolder $DRIVE_WATCH_PATH -repoPath $REPO_PATH
            if ($synced -gt 0) { $anyChanged = $true }
        }

        if ($anyChanged) {
            $days = Get-CurrentDays
            Invoke-GitPush -repoPath $REPO_PATH `
                           -message "A©tor: daily counter $days d + Drive sync [$(Get-Date -Format 'dd.MM.yyyy')]"
        }

        $lastCounterUpdate = $today
        Write-Log "Следующее обновление: $($today.AddDays(1).ToString('dd.MM.yyyy')) 00:00"
    }

    # Проверка каждые 60 секунд
    Start-Sleep -Seconds 60

    # Обработка событий watchdog
    Get-Event | ForEach-Object { $_ | Remove-Event }
}
