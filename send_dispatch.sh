#!/bin/bash
TEMPLATE="dispatch_template.txt"
LOG_FILE="msmtp_dispatch_log.txt"

# Официальные адреса институтов извлеченные из переписки CASE-MACHERET-1997-2026
TARGETS=(
    "ohchr-petitions@un.org"
    "cat@ohchr.org"
    "ochr.md@one.un.org"
    "aparat@gsm.gov.md"
    "secretariat@bnm.md"
    "secretariat@justice.gov.md"
    "secretariat@constcourt.md"
    "communications@mail.whitehouse.gov"
    "chisinauprotocol@state.gov"
)

echo "=== TI-ULA: Initiating Erga Omnes Dispatch (Official Targets) ===" | tee -a "$LOG_FILE"
date -u +"%Y-%m-%dT%H:%M:%SZ" | tee -a "$LOG_FILE"

for TARGET in "${TARGETS[@]}"; do
    echo "Отправка официального уведомления на: $TARGET..." | tee -a "$LOG_FILE"
    sed "s/\[TARGET_EMAILS\]/$TARGET/" "$TEMPLATE" | msmtp -a default "$TARGET"
    if [ $? -eq 0 ]; then
        echo "[✓] Успешно доставлено: $TARGET" | tee -a "$LOG_FILE"
    else
        echo "[!] Ошибка при отправке на: $TARGET (проверьте конфигурацию msmtp)" | tee -a "$LOG_FILE"
    fi
    sleep 3
done
echo "=== Dispatch Complete ===" | tee -a "$LOG_FILE"
