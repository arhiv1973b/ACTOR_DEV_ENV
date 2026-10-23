#!/bin/bash
# ⚖ [A©tor Declaration] Full Repository Backup & Integrity Anchor (Jus Cogens Scope)

# Убеждаемся, что находимся в корне репозитория
if [ ! -d ".git" ]; then
  echo "Критическая ошибка: Запустите скрипт из корня репозитория (где находится папка .git)."
  exit 1
fi

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
# Создаем папку для бэкапов на уровень выше репозитория, чтобы архив не попал сам в себя
BACKUP_DIR="../ACTOR_SECURE_BACKUPS"
ARCHIVE_NAME="ACTOR_DEV_ENV_L1_State_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"

echo "⚖ Инициализация создания неизменяемого слепка канонического депонита..."
mkdir -p "$BACKUP_DIR"

# Архивация всей рабочей директории и крипто-манифестов
tar -czf "$ARCHIVE_PATH" --exclude="node_modules" .

echo "Вычисление SHA-256 инварианта архива..."
cd "$BACKUP_DIR" || exit
sha256sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.sha256"

echo -e "\n=== Бэкап успешно зафиксирован ==="
echo "Локация архива: $(realpath "$ARCHIVE_NAME")"
echo "Хэш архива: $(cat "${ARCHIVE_NAME}.sha256")"
echo "A©TOR_KEY=\"# [⚖ A©tor Declaration]\""
