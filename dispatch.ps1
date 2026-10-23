# ==============================================================================
# PIPELINE: DUDO & ART. 4 CONST. RM AUTOMATED DISPATCH (PowerShell Version)
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "[1/5] Криптографическая подготовка и хеширование манифеста..." -ForegroundColor Cyan
$HashResult = Get-FileHash -Path "dispatch_payload.json" -Algorithm SHA256
$HashString = "$($HashResult.Hash.ToLower())  dispatch_payload.json"
Set-Content -Path "hash.txt" -Value $HashString -Encoding utf8
Write-Host "[OK] SHA-256 Hash generated: $($HashResult.Hash)" -ForegroundColor Green

Write-Host "[2/5] Криптографическая подпись (GPG)..." -ForegroundColor Cyan
try {
    gpg --sign --armor dispatch_payload.json
} catch {
    Write-Host "[WARN] GPG signing skipped or failed, proceeding with cryptographic hash anchor." -ForegroundColor Yellow
}

Write-Host "[3/5] Запуск боевой рассылки с запросом квитанций DSN (SMTP 250 OK)..." -ForegroundColor Cyan
python erga_omnes_mail_dispatcher.py --payload dispatch_payload.json --execute --require-dsn

Write-Host "[4/5] Аудит и проверка логов доставки..." -ForegroundColor Cyan
if (Test-Path "audit_log.json") {
    Write-Host "[OK] Audit log verified." -ForegroundColor Green
} else {
    throw "Audit log not found!"
}

Write-Host "[5/5] Неизменяемая фиксация в Git Ledger (GitHub)..." -ForegroundColor Cyan
git add dispatch_payload.json audit_log.json hash.txt
$CommitMsg = "dispatch(dudo): automatic PowerShell pipeline execution - DUDO privilege & Art.4 Const. RM invocation"
git commit -m $CommitMsg
git push origin feature/cyber-sabotage-audit-10-2026

Write-Host "[SUCCESS] Полный цикл рассылки, аудита и фиксации (DUDO / Erga Omnes) успешно завершен." -ForegroundColor Green
