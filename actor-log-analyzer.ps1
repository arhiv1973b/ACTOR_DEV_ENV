param(
    [Parameter(Mandatory=$true)]
    [string]$LogFilePath,

    [Parameter(Mandatory=$false)]
    [int]$LinesPerBatch = 30,

    [Parameter(Mandatory=$false)]
    [int]$DelaySeconds = 5,

    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "H:\ACTOR_DEV_ENV\recovery_plan.md"
)

# Проверка наличия файла
if (-not (Test-Path $LogFilePath)) {
    Write-Error ">>> [A©t0r] ОШИБКА: Файл $LogFilePath не найден."
    return
}

$lines = Get-Content -Path $LogFilePath
$totalLines = $lines.Count
$batches = [math]::Ceiling($totalLines / $LinesPerBatch)

Write-Host ">>> [A©t0r] Инициализация пакетного анализа логов." -ForegroundColor Cyan
Write-Host "Файл: $LogFilePath | Строк: $totalLines | Пакетов: $batches" -ForegroundColor Cyan
Write-Host "Результаты будут сохранены в: $OutputFile`n" -ForegroundColor Cyan

# Инициализация файла отчета
"### A©tor Log Recovery Analysis - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" | Out-File -FilePath $OutputFile -Encoding UTF8

for ($i = 0; $i -lt $batches; $i++) {
    $start = $i * $LinesPerBatch
    $end = [math]::Min(($start + $LinesPerBatch - 1), ($totalLines - 1))
    $chunk = $lines[$start..$end] -join "`n"

    $systemPrompt = "Действуй как A©t0r. Проанализируй этот фрагмент лога ($($i+1)/$batches), выяви причины ошибок окружения/кода и дай точные команды для ремонта без лишних рассуждений:`n`n"
    
    # Формирование и очистка строки для безопасной передачи в внешний EXE
    $fullPrompt = $systemPrompt + $chunk
    $safePrompt = $fullPrompt -replace '"', '\"'

    Write-Host ">>> [A©t0r] Отправка пакета $($i+1) из $batches в Gemini CLI..." -ForegroundColor Yellow

    # Запись заголовка пакета в отчет
    "`n#### Пакет $($i+1)/$batches`n" | Out-File -FilePath $OutputFile -Append -Encoding UTF8

    # Вызов Gemini CLI (перехват вывода)
    $response = gemini -m gemini-3.5-flash -p "$safePrompt"

    # Вывод в консоль и запись в файл
    $response | Out-Host
    $response | Out-File -FilePath $OutputFile -Append -Encoding UTF8

    # Пауза для предотвращения блокировок API (Rate Limiting)
    if ($i -lt ($batches - 1)) {
        Write-Host ">>> [A©t0r] Ожидание $DelaySeconds сек. (защита от Rate Limit)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds $DelaySeconds
    }
}

Write-Host "`n>>> [A©t0r] Анализ завершен. План восстановления собран в $OutputFile" -ForegroundColor Green