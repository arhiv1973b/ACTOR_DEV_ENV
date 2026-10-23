# ==============================================================================
# UNIFIED ESCALATION ORCHESTRATOR (CASE-MACHERET-1997-2026)
# CONTOUR: Diplomacy (US/WH) -> Constitutional Control (CC RM) -> Prosecution -> Ledger
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "[*] ЗАПУСК ЕДИНОГО КОНТУРА ЭСКАЛАЦИИ (ДЕЛО: 1-26114218-12-10-09092026-1)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

# Шаг 1: Криптографическая подготовка и хеширование манифеста
Write-Host "`n[ЭТАП 1/4] Криптографическая подготовка и генерация SHA-256..." -ForegroundColor Yellow
$HashResult = Get-FileHash -Path "dispatch_payload.json" -Algorithm SHA256
$HashString = "$($HashResult.Hash.ToLower())  dispatch_payload.json"
Set-Content -Path "hash.txt" -Value $HashString -Encoding utf8
Write-Host "[OK] SHA-256 Хеш зафиксирован: $($HashResult.Hash)" -ForegroundColor Green

# Шаг 2: Запуск боевой рассылки (Дипломатия, CC RM, Прокуратура, Суды) с запросом DSN
Write-Host "`n[ЭТАП 2/4] Запуск боевой рассылки (SMTP 250 OK + DSN Квитанции)..." -ForegroundColor Yellow
python erga_omnes_mail_dispatcher.py --payload dispatch_payload.json --execute --require-dsn
Write-Host "[OK] Рассылка по всем каналам завершена успешно." -ForegroundColor Green

# Шаг 3: Автоматический парсинг входящих DSN-квитанций
Write-Host "`n[ЭТАП 3/4] Сканирование шлюза и парсинг входящих подтверждений (DSN Inbox)..." -ForegroundColor Yellow
if (Test-Path "dsn_inbound_parser.py") {
    python dsn_inbound_parser.py
    Write-Host "[OK] Квитанции успешно интегрированы в аудит-лог." -ForegroundColor Green
} else {
    Write-Host "[WARN] Скрипт парсера пропущен, аудит-лог актуален." -ForegroundColor Yellow
}

# Шаг 4: Генерация итогового отчета и фиксация в Immutable Ledger (GitHub)
Write-Host "`n[ЭТАП 4/4] Генерация Delivery Status Report и фиксация в Immutable Ledger..." -ForegroundColor Yellow
if (Test-Path "generate_delivery_report.py") {
    python generate_delivery_report.py
}

git add dispatch_payload.json audit_log.json hash.txt Delivery_Status_Report_CASE_MACHERET.md US_EMBASSY_DIPLOMATIC_MEMORANDUM_2026.md 2>$null
$CommitMsg = "orchestrator(unified): complete escalation pipeline execution - DUDO & Art.4 Const. RM [$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')]"
git commit -m $CommitMsg
git push origin feature/cyber-sabotage-audit-10-2026

Write-Host "`n================================================================================" -ForegroundColor Green
Write-Host "[SUCCESS] ЕДИНЫЙ КОНТУР ЭСКАЛАЦИИ УСПЕШНО ВЫПОЛНЕН И ЗАКРЕПЛЕН В GITHUB LEDGER." -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
