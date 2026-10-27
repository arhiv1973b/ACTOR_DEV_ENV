# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

# 1. Задаем параметры адресата и путей
$Recipient = "arhiv240@gmail.com"
$NotifierPath = Join-Path -Path $env:LOCALAPPDATA -ChildPath "ActorAlertNotifier.ps1"
$TempMailFile = Join-Path -Path $env:TEMP -ChildPath "ti_ula_alert_mail.txt"

# 2. Извлечение свежайшего события ID 1001 из Event Viewer
$Event = Get-WinEvent -FilterHashtable @{
    LogName = 'Application'
    ProviderName = 'TI-ULA-Watchdog', 'TI-ULA-Healer'
    Id = 1001
} -MaxEvents 1 -ErrorAction SilentlyContinue

if ($Event) {
    $EventTime = $Event.TimeCreated.ToString("yyyy-MM-dd HH:mm:ss")
    $EventDetails = $Event.Message
} else {
    $EventTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $EventDetails = "Зафиксирован факт срабатывания триггера 1001 (детали события еще не зафиксированы в кеше)."
}

# 3. Формирование тела письма с заголовками для msmtp
$Subject = "[SECURITY ALERT 1001] TI-ULA Tampering Detected"

$EmailMessage = @"
To: $Recipient
Subject: $Subject
Content-Type: text/plain; charset=UTF-8

======================================================================
[ALERT] ЗАФИКСИРОВАНО ВМЕШАТЕЛЬСТВО В АРХИТЕКТУРУ TI-ULA (EVENT 1001)
======================================================================
Субъект права: A©tor (A©t0r) / CASE-MACHERET-1997-2026
Время инцидента: $EventTime
Компьютер: $env:COMPUTERNAME
Учетная запись: $env:USERNAME

СОДЕРЖАНИЕ ИНЦИДЕНТА ИЗ ЖУРНАЛА СОБЫТИЙ:
----------------------------------------------------------------------
$EventDetails
----------------------------------------------------------------------

ПРАВОВОЙ ПЕРИМЕТР:
- Всеобщая декларация прав человека 1948 г. (ВДПЧ / DUDO)
- Императивные нормы международного права (Jus Cogens) и Erga Omnes
- Конституция Республики Молдова (ст. 4, 47, 51)

СТАТУС: Запущен автоматический протокол регенерации и восстановления демона.
======================================================================
"@

# 4. Запись сообщения во временный файл в кодировке UTF-8 без BOM
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($TempMailFile, $EmailMessage, $Utf8NoBom)

# 5. Поиск бинарного файла msmtp в системах и отправка
$MsmtpCmd = Get-Command msmtp -ErrorAction SilentlyContinue

if ($MsmtpCmd) {
    Get-Content $TempMailFile -Encoding UTF8 | & $MsmtpCmd.Source -t
    Write-Host "Alert email successfully queued/sent to $Recipient via msmtp." -ForegroundColor Green
} else {
    $FallbackMsmtp = "C:\msmtp\msmtp.exe"
    if (Test-Path $FallbackMsmtp) {
        Get-Content $TempMailFile -Encoding UTF8 | & $FallbackMsmtp -t
        Write-Host "Alert email successfully sent using fallback msmtp path." -ForegroundColor Green
    } else {
        Write-Host "ОШИБКА: msmtp не найден в PATH или по пути C:\msmtp\msmtp.exe" -ForegroundColor Red
    }
}

# 6. Очистка временных данных
if (Test-Path $TempMailFile) {
    Remove-Item -Path $TempMailFile -Force
}
