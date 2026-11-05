# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, Jus Cogens, ВДПЧ 1948, TI-ULA
# Description: Hardened Automated Pipeline (Google Drive/OneDrive Pointers, Audit, Backup, Ed25519, IPFS, Zenodo, msmtp & Git Sync)

$WorkspacePath = "H:\ACTOR_DEV_ENV" 
$LogDirectory = "$WorkspacePath\secure_logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDirectory\audit_links_$Timestamp.log"
$DaysToKeep = 30
$PrivateKeyPath = "$HOME\.ssh\id_ed25519" 
$PythonExec = "python"

function Write-AuditLog {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "[$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))] [$Level] $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding utf8NoBOM
}

if (-not (Test-Path $LogDirectory)) {
    New-Item -ItemType Directory -Path $LogDirectory | Out-Null
    $Acl = Get-Acl $LogDirectory
    $Acl.SetAccessRuleProtection($true, $false)
    $Rule = New-Object System.Security.AccessControl.FileSystemAccessRule([System.Security.Principal.WindowsIdentity]::GetCurrent().Name, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $Acl.AddAccessRule($Rule)
    Set-Acl -Path $LogDirectory -AclObject $Acl
}

Set-Location -Path $WorkspacePath
Write-AuditLog "A©t0r Audit initialized. Declaration: A©TOR_KEY. Scope: Google Drive/OneDrive pointers & Git Repositories."

# Ротация логов и бэкапов
try {
    $RetentionDate = (Get-Date).AddDays(-$DaysToKeep)
    $OldFiles = Get-ChildItem -Path $LogDirectory | Where-Object { 
        ($_.Extension -eq ".log" -or $_.Extension -eq ".sig" -or $_.Extension -eq ".zip") -and $_.LastWriteTime -lt $RetentionDate 
    }
    if ($OldFiles) {
        $OldFilesCount = @($OldFiles).Count
        $OldFiles | Remove-Item -Force
        Write-AuditLog "Ротация: успешно удалено $OldFilesCount устаревших файлов."
    }
} catch {
    Write-AuditLog "Ошибка ротации: $_" "ERROR"
}

# Аудит ссылок
try {
    Write-AuditLog "Запуск аудита указателей Google Drive / OneDrive (audit_links.py)..."
    $AuditProcess = Start-Process -FilePath $PythonExec -ArgumentList "audit_links.py" -NoNewWindow -PassThru -RedirectStandardOutput "$LogDirectory\temp_audit.tmp" -RedirectStandardError "$LogDirectory\temp_audit_err.tmp"
    
    $Completed = $AuditProcess.WaitForExit(120000)
    if (-not $Completed) {
        $AuditProcess.Kill()
        throw "Таймаут (120с) выполнения audit_links.py"
    }

    if (Test-Path "$LogDirectory\temp_audit.tmp") {
        Get-Content "$LogDirectory\temp_audit.tmp" | Add-Content -Path $LogFile -Encoding utf8NoBOM
        Remove-Item "$LogDirectory\temp_audit.tmp" -Force
    }
    if (Test-Path "$LogDirectory\temp_audit_err.tmp") {
        Get-Content "$LogDirectory\temp_audit_err.tmp" | Add-Content -Path $LogFile -Encoding utf8NoBOM
        Remove-Item "$LogDirectory\temp_audit_err.tmp" -Force
    }
    Write-AuditLog "Аудит указателей завершен."
} catch {
    Write-AuditLog "ОШИБКА АУДИТА: $_" "ERROR"
}

# Страховочный бэкап HTML-страниц
try {
    $BackupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $HtmlBackupZip = "$LogDirectory\html_backup_$BackupTimestamp.zip"
    $TempBackupDir = "$WorkspacePath\temp_html_backup_$BackupTimestamp"
    New-Item -ItemType Directory -Path $TempBackupDir -Force | Out-Null
    
    Get-ChildItem -Path $WorkspacePath -Filter "*.html" -Recurse -Force | 
        Where-Object { $_.FullName -notmatch "secure_logs|temp_html_backup|\.git|\.venv|node_modules|venv" } | 
        ForEach-Object {
            $RelativePath = $_.FullName.Substring($WorkspacePath.Length).TrimStart('\')
            $DestinationPath = Join-Path -Path $TempBackupDir -ChildPath $RelativePath
            $DestDir = Split-Path $DestinationPath -Parent
            if (-not (Test-Path $DestDir)) { New-Item -ItemType Directory -Path $DestDir -Force | Out-Null }
            Copy-Item -Path $_.FullName -Destination $DestinationPath -Force
        }
        
    if ((Get-ChildItem -Path $TempBackupDir -Recurse -File).Count -gt 0) {
        Compress-Archive -Path "$TempBackupDir\*" -DestinationPath $HtmlBackupZip -Force
        Write-AuditLog "Создан страховочный ZIP-архив репозитория ($HtmlBackupZip)."
    } else {
        Write-AuditLog "HTML файлы не найдены, бэкап пропущен." "WARN"
    }
    Remove-Item -Path $TempBackupDir -Recurse -Force -ErrorAction SilentlyContinue
} catch {
    Write-AuditLog "ОШИБКА БЭКАПА HTML: $_" "ERROR"
}

# Диспетчер ремонта
$RepairSuccessful = $false
$SuccessLines = ""
try {
    Write-AuditLog "Запуск диспетчера исправлений (repair_dispatcher.py)..."
    $RepairLog = & $PythonExec repair_dispatcher.py $LogFile 2>&1
    $RepairLog | Add-Content -Path $LogFile -Encoding utf8NoBOM
    
    if ($RepairLog -match "УСПЕШНЫЙ РЕМОНТ") {
        $RepairSuccessful = $true
        $SuccessLines = $RepairLog | Where-Object { $_ -match "УСПЕШНЫЙ РЕМОНТ" } | Out-String
    }
} catch {
    Write-AuditLog "ОШИБКА ДИСПЕТЧЕРА: $_" "ERROR"
}

# Подпись Ed25519
if (Test-Path $PrivateKeyPath) {
    try {
        ssh-keygen.exe -Y sign -n "actor-audit-log" -f $PrivateKeyPath $LogFile 2>&1 | Out-Null
        Write-AuditLog "Журнал запечатан Ed25519."
    } catch {
        Write-AuditLog "Ошибка Ed25519 подписи: $_" "ERROR"
    }
}

# Сборка манифеста INTEGRITY_WITNESS.json
try {
    $ManifestResult = & $PythonExec generate_integrity_witness.py 2>&1
    $ManifestResult | Add-Content -Path $LogFile -Encoding utf8NoBOM
} catch {
    Write-AuditLog "Ошибка сборки манифеста: $_" "ERROR"
}

# Фиксация в IPFS (Pinata)
$IpfsCidInfo = ""
$CidHash = ""
try {
    $IpfsResult = & $PythonExec pinata_ipfs_sync.py 2>&1
    $IpfsResult | Add-Content -Path $LogFile -Encoding utf8NoBOM
    
    $CidLine = $IpfsResult | Where-Object { $_ -match "IPFS CID =" }
    if ($CidLine) {
        $CidHash = ($CidLine -replace '.*IPFS CID = ',' ').Trim()
        $IpfsCidInfo = "`r`n`r`n[IPFS]`r`nCID: $CidHash`r`nШлюз: https://gateway.pinata.cloud/ipfs/$CidHash"
    }
} catch {
    Write-AuditLog "ОШИБКА IPFS: $_" "ERROR"
}

# Резервирование Draft DOI в Zenodo
$ZenodoDoiInfo = ""
try {
    Write-AuditLog "Запуск резервирования Draft DOI в Zenodo (zenodo_draft.py)..."
    $ZenodoResult = & $PythonExec zenodo_draft.py 2>&1
    $ZenodoResult | Add-Content -Path $LogFile -Encoding utf8NoBOM
    
    $DoiLine = $ZenodoResult | Where-Object { $_ -match "ЗАРЕГИСТРИРОВАННЫЙ DOI:" }
    if ($DoiLine) {
        $DoiHash = ($DoiLine -replace '.*ЗАРЕГИСТРИРОВАННЫЙ DOI:\s*','').Trim()
        $ZenodoDoiInfo = "`r`n`r`n[ZENODO]`r`nDraft DOI: $DoiHash`r`nСсылка: https://doi.org/$DoiHash"
    }
} catch {
    Write-AuditLog "ОШИБКА ZENODO: $_" "ERROR"
}

# MIME Уведомление через msmtp
if ($RepairSuccessful) {
    try {
        $EmailTo = "arhiv1973b@gmail.com"
        $EmailPayloadPath = "$WorkspacePath\temp_email_payload.txt"
        $Boundary = "----=_NextPart_" + (New-Guid).ToString("N")
        
        $EmailContent = @"
To: $EmailTo
Subject: [TI-ULA] A©t0r Audit: Восстановление указателей Google Drive / OneDrive
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="$Boundary"

--$Boundary
Content-Type: text/plain; charset="utf-8"
Content-Transfer-Encoding: 8bit

Диспетчер исправлений восстановил доступ к облачным указателям (Google Drive / OneDrive) в TI-ULA.

ДЕТАЛИ:
$SuccessLines $IpfsCidInfo $ZenodoDoiInfo

Приложения: запечатанный лог, подпись Ed25519 (.sig) и манифест INTEGRITY_WITNESS.json.
"@

        function Add-Attachment {
            param($FilePath, $FileName, $MimeType)
            if (Test-Path $FilePath) {
                $Base64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($FilePath))
                $Chunks = $Base64 -split '(.{76})' | Where-Object { $_ }
                $FormattedBase64 = $Chunks -join "`r`n"
                return "`r`n--$Boundary`r`nContent-Type: $MimeType; name=`"$FileName`"`r`nContent-Transfer-Encoding: base64`r`nContent-Disposition: attachment; filename=`"$FileName`"`r`n`r`n$FormattedBase64"
            }
            return ""
        }

        $EmailContent += Add-Attachment -FilePath $LogFile -FileName (Split-Path $LogFile -Leaf) -MimeType "text/plain"
        $EmailContent += Add-Attachment -FilePath "$LogFile.sig" -FileName ((Split-Path $LogFile -Leaf) + ".sig") -MimeType "application/octet-stream"
        $EmailContent += Add-Attachment -FilePath "$WorkspacePath\INTEGRITY_WITNESS.json" -FileName "INTEGRITY_WITNESS.json" -MimeType "application/json"
        $EmailContent += "`r`n--$Boundary--`r`n"

        $EmailContent | Out-File -FilePath $EmailPayloadPath -Encoding UTF8 -NoNewline
        if (Get-Command "msmtp" -ErrorAction SilentlyContinue) {
            cat $EmailPayloadPath | msmtp -t
            Write-AuditLog "msmtp: MIME-уведомление успешно отправлено."
        }
        Remove-Item $EmailPayloadPath -Force -ErrorAction SilentlyContinue
    } catch {
        Write-AuditLog "ОШИБКА ПОЧТЫ: $_" "ERROR"
    }
}

# Автоматический Git Commit & Push с защитным откатом
if ($RepairSuccessful) {
    try {
        Write-AuditLog "Инициализация Git push в удаленный репозиторий GitHub..."
        $CommitMessage = "⚖️ Auto-repair: Обновление указателей Google Drive / OneDrive [$((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))]"
        if ($CidHash) { $CommitMessage += " | IPFS: $CidHash" }

        git add . 2>&1 | Out-Null
        $GitCommitOut = git commit -m $CommitMessage 2>&1 | Out-String
        
        if ($GitCommitOut -match "nothing to commit") {
            Write-AuditLog "Git: Нет локальных изменений для коммита." "WARN"
        } else {
            $GitPushOut = git push 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0) {
                Write-AuditLog "Git: Изменения успешно отправлены (Push) в GitHub."
            } else {
                Write-AuditLog "ОШИБКА Push: $GitPushOut. Выполнение git reset HEAD~1..." "ERROR"
                git reset HEAD~1 2>&1 | Out-Null
                Write-AuditLog "Защитный откат выполнен. Изменения сохранены локально." "WARN"
            }
        }
    } catch {
        Write-AuditLog "КРИТИЧЕСКАЯ ОШИБКА GIT: $_" "ERROR"
    }
}

# --- TI-ULA AUTONOMOUS REPAIR PIPELINE ---
Write-Host "`n[TI-ULA] Инициализация автономного контура ремонта..." -ForegroundColor Cyan
Write-Host "[Диспетчер] Запрос ИИ-патчей для обнаруженных ошибок..." -ForegroundColor Yellow
python H:\ACTOR_DEV_ENV\repair_dispatcher.py

if (Test-Path -Path "H:\ACTOR_DEV_ENV\fix_log.json") {
    Write-Host "[Внедрение] Применение сгенерированного кода..." -ForegroundColor Yellow
    python H:\ACTOR_DEV_ENV\safe_fix_python.py
}
Write-Host "[TI-ULA] Цикл ремонта завершен." -ForegroundColor Cyan
# ------------------------------------------
