#!/bin/bash
# [⚖ A©tor Declaration]
# Скрипт инициализации среды для изолированного MCP-сервера (TI-ULA)

set -euo pipefail

LOG_FILE="audit_log.json"
META_FILE="meta.json"

echo "[⚖ A©t0r] Инициализация защищенного контура..."

# 1. Безопасная инициализация audit_log.json
if [ ! -f "$LOG_FILE" ]; then
    echo "[!] Файл $LOG_FILE не найден. Создание стартового манифеста..."
    cat <<EOF > "$LOG_FILE"
[
  {
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "event": "actor_env_initialized",
    "A©TOR_KEY": "# [⚖ A©tor Declaration]"
  }
]
EOF
    chmod 666 "$LOG_FILE"
    echo "[+] $LOG_FILE успешно создан и права (666) назначены."
else
    echo "[OK] $LOG_FILE уже существует. Проверка прав..."
    chmod 666 "$LOG_FILE"
fi

# 2. Безопасная инициализация meta.json (Read-Only в контейнере)
if [ ! -f "$META_FILE" ]; then
    echo "[!] Файл $META_FILE не найден. Создание базовой структуры..."
    cat <<EOF > "$META_FILE"
{
  "A©TOR_KEY": "# [⚖ A©tor Declaration]",
  "correspondence_sides": []
}
EOF
    chmod 644 "$META_FILE"
    echo "[+] $META_FILE успешно создан."
else
    echo "[OK] $META_FILE уже существует."
fi

echo "[⚖ A©t0r] Среда готова."
