#!/bin/bash
# ⚖ [A©tor Declaration] Deterministic HTML Checksum Verifier (Jus Cogens Scope)

TARGET_FILE="case_maceret_appeal_20261023.html"
EXPECTED_HASH="7a4c4c6d44be963c9d673e2d48975ed49ecfaec02e7527810e3f39de27afdb68"

if [ ! -f "$TARGET_FILE" ]; then
  echo "Критическая ошибка: Файл $TARGET_FILE не найден."
  exit 1
fi

echo "⚖ Вычисление SHA-256 хэша для $TARGET_FILE..."

# Вычисляем хэш без учета строки комментария checksum
CURRENT_HASH=$(python3 -c "
import hashlib
with open('$TARGET_FILE', 'r', encoding='utf-8') as f:
    text = f.read()
lines = [l for l in text.splitlines() if 'checksum:' not in l]
clean_text = '\n'.join(lines)
print(hashlib.sha256(clean_text.encode('utf-8')).hexdigest())
")

echo "Текущий хэш:  $CURRENT_HASH"
echo "Ожидаемый хэш: $EXPECTED_HASH"

if [ "$CURRENT_HASH" = "$EXPECTED_HASH" ]; then
  echo "✅ Целостность подтверждена: Хэши полностью совпадают."
  exit 0
else
  echo "❌ Ошибка: Обнаружено расхождение хэшей! Возможна потеря символов или несанкционированная правка."
  exit 1
fi
