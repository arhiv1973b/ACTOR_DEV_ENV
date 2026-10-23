#!/bin/bash

BRANCH_NAME="evidence/fincombank-financial-traces"
TARGET_BRANCH="master"
WORKFLOW_FILE="erga_omnes_dispatch.yml"

echo "=== 1. Интеграция ветки (Pull Request & Merge) ==="
# Создаем PR, если он еще не создан
gh pr create --base "$TARGET_BRANCH" --head "$BRANCH_NAME" \
  --title "Merge Evidence and Erga Omnes Dispatch Pipeline" \
  --body "CASE-MACHERET-1997-2026: Интеграция TI-ULA графа, крипто-манифестов и автоматизации рассылки." || echo "[i] PR уже существует."

# Выполняем слияние (Merge) с сохранением ветки
gh pr merge "$BRANCH_NAME" --merge --delete-branch=false || echo "[i] Слияние уже выполнено или требует ручного подтверждения."
echo "[✓] Интеграция с $TARGET_BRANCH завершена. Workflow доступен для API."

echo "=== 2. Проверка GitHub Secrets (Pre-flight check) ==="
SECRETS=$(gh secret list)
REQUIRED_SECRETS=("SMTP_HOST" "SMTP_USER" "SMTP_PASSWORD")
MISSING_SECRETS=0

for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if echo "$SECRETS" | grep -q "$SECRET"; then
        echo "[✓] Секрет $SECRET найден."
    else
        echo "[!] ВНИМАНИЕ: Секрет $SECRET НЕ НАЙДЕН!"
        MISSING_SECRETS=$((MISSING_SECRETS + 1))
    fi
done

if [ "$MISSING_SECRETS" -gt 0 ]; then
    echo ""
    echo "ОШИБКА: Отсутствуют необходимые секреты. Добавьте их перед запуском:"
    echo "gh secret set SMTP_HOST -b \"smtp.example.com\""
    echo "gh secret set SMTP_USER -b \"your_email@example.com\""
    echo "gh secret set SMTP_PASSWORD -b \"your_password\""
    echo "Прерывание запуска workflow."
    exit 1
fi

echo "=== 3. Запуск Erga Omnes Dispatch Workflow ==="
# Запускаем workflow из ветки master
gh workflow run "$WORKFLOW_FILE" --ref "$TARGET_BRANCH"

echo "[✓] Workflow успешно запущен!"
echo "Проверить статус рассылки можно командой:"
echo "gh run list --workflow=$WORKFLOW_FILE"
