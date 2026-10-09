# ==============================================================================
# DUAL-STEP ESCALATION: US EMBASSY DISPATCH + CC RM REPORT
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "[STEP 1/2] Боевая рассылка в Посольство США и международные контуры..." -ForegroundColor Cyan
python erga_omnes_mail_dispatcher.py --payload dispatch_payload.json --execute --require-dsn

Write-Host "[STEP 2/2] Генерация и фиксация Delivery Status Report для Конституционного суда РМ..." -ForegroundColor Cyan
python generate_delivery_report.py

Write-Host "[SUCCESS] Двойной контур эскалации выполнен и зафиксирован." -ForegroundColor Green
