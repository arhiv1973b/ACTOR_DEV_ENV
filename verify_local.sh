#!/bin/bash
# ⚖ [A©tor Declaration] Local Crypto-Audit Script (Jus Cogens Scope)

MANIFEST_DIR="05_CRYPTO_MANIFESTS"
PUB_KEY="actor_public_ed25519.pem" # Замени на актуальное имя твоего публичного ключа

echo "⚖ Инициализация аудита: SHA-256 и Ed25519"
echo "Target: $MANIFEST_DIR"

if [ ! -d "$MANIFEST_DIR" ]; then
  echo "Критическая ошибка: Директория $MANIFEST_DIR не найдена."
  exit 1
fi

cd "$MANIFEST_DIR" || exit

echo -e "\n=== 1. Инвариант SHA-256 ==="
if [ -f "sha256sums.txt" ]; then
  # Строгая проверка по эталонному манифесту
  sha256sum -c sha256sums.txt
else
  echo "Манифест sha256sums.txt отсутствует. Вычисляю контрольные суммы артефактов:"
  for file in *; do
    if [ -f "$file" ]; then
      sha256sum "$file"
    fi
  done
fi

echo -e "\n=== 2. Верификация Ed25519 (L0 Authority) ==="
if [ ! -f "$PUB_KEY" ]; then
  echo "Внимание: Публичный ключ $PUB_KEY не найден в текущей директории."
else
  shopt -s nullglob
  for sig in *.sig; do
    target="${sig%.sig}"
    if [ -f "$target" ]; then
      echo -n "Верификация $target: "
      # Проверка сырой подписи Ed25519
      openssl pkeyutl -verify -pubin -inkey "$PUB_KEY" -rawin -in "$target" -sigfile "$sig"
    else
      echo "Сбой: Исходный файл $target для подписи $sig отсутствует (нарушение графа)."
    fi
  done
fi
echo -e "\nАудит завершен. Канонический статус проверен."
