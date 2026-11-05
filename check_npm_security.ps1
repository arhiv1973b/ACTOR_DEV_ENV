<#
.SYNOPSIS
    Скрипт проверки безопасности npm-зависимостей для контура TI-ULA.
.DESCRIPTION
    Выполняет npm audit, сохраняет отчеты в директорию secure_logs/
    и выводит сводку по уязвимостям (Critical, High, Moderate, Low).
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "[TI-ULA SECURITY] Запуск аудита npm-зависимостей..." -ForegroundColor Cyan

# Проверка наличия node/npm
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "[ОШИБКА] npm не найден в системе. Убедитесь, что Node.js установлен." -ForegroundColor Red
    exit 1
}

$reportDir = "secure_logs"
if (!(Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportJson = Join-Path $reportDir "npm_audit_$timestamp.json"
$reportTxt = Join-Path $reportDir "npm_audit_$timestamp.log"

Write-Host "[1/3] Выполнение npm audit с экспортом в JSON..." -ForegroundColor Yellow
try {
    # Сохраняем JSON-отчет (без BOM)
    $auditJsonOutput = npm audit --json
    $auditJsonOutput | Set-Content -Path $reportJson -Encoding utf8
    Write-Host "[OK] JSON-отчет сохранен в $reportJson" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Не удалось полностью выполнить npm audit --json." -ForegroundColor Yellow
}

Write-Host "[2/3] Формирование текстового лога..." -ForegroundColor Yellow
npm audit > $reportTxt 2>&1
Write-Host "[OK] Текстовый лог сохранен в $reportTxt" -ForegroundColor Green

Write-Host "[3/3] Анализ результатов и формирование сводки..." -ForegroundColor Yellow
if (Test-Path $reportJson) {
    try {
        $jsonContent = Get-Content $reportJson -Raw
        if ($jsonContent) {
            $auditData = $jsonContent | ConvertFrom-Json
            if ($auditData.metadata -and $auditData.metadata.vulnerabilities) {
                $v = $auditData.metadata.vulnerabilities
                Write-Host "`n========================================" -ForegroundColor Cyan
                Write-Host " СВОДКА УЯВИМОСТЕЙ NPM AUDIT:" -ForegroundColor White
                Write-Host "   Критические (Critical) : $($v.critical)" -ForegroundColor Red
                Write-Host "   Высокие (High)         : $($v.high)" -ForegroundColor Yellow
                Write-Host "   Средние (Moderate)     : $($v.darkYellow)" -ForegroundColor DarkYellow
                Write-Host "   Низкие (Low)           : $($v.low)" -ForegroundColor Gray
                Write-Host "   Всего уязвимостей      : $($v.total)" -ForegroundColor Magenta
                Write-Host "========================================`n" -ForegroundColor Cyan
            }
        }
    } catch {
        Write-Host "[INFO] Текстовый формат отчета доступен в файле $reportTxt" -ForegroundColor Gray
    }
}

Write-Host "[ГОТОВО] Проверка безопасности завершена. Артефакты изолированы в '$reportDir\'." -ForegroundColor Green
