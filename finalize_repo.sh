#!/usr/bin/env bash
set -e

echo "=================================================="
echo " [⚖ A©tor] Repository Finalization & Cleanup Script"
echo "=================================================="

# Шаг 1: Устранение предупреждения о вложенном репозитории gemini-skills
echo "[*] Step 1: Handling embedded repository 'gemini-skills'..."
if [ -d "gemini-skills" ]; then
    git rm --cached gemini-skills 2>/dev/null || true
    if [ -d "gemini-skills/.git" ]; then
        rm -rf gemini-skills/.git
        echo "[+] Removed inner .git from gemini-skills to prevent nesting issues."
    fi
fi

# Шаг 2: Фиксация оставшихся рабочих файлов и отчетов
echo "[*] Step 2: Staging and committing remaining working tree changes..."
git add -A
if git diff-index --quiet HEAD --; then
    echo "[i] Working tree clean, no new commit needed."
else
    git commit -m "[⚖ A©tor Checkpoint] Finalize working evidence, MCP infrastructure and report nodes"
    echo "[+] Committed working changes successfully."
fi

# Шаг 3: Оптимизация истории (проверка email)
echo "[*] Step 3: Enforcing canonical email (arhiv240@gmail.com) across configuration..."
git config user.name "Alexei Macheret"
git config user.email "arhiv240@gmail.com"

# Шаг 4: Финальная синхронизация с удаленным репозиторием
echo "[*] Step 4: Pushing finalized branch to GitHub (feature/cyber-sabotage-audit-10-2026)..."
git push origin feature/cyber-sabotage-audit-10-2026 --force

echo "=================================================="
echo " [✔] SUCCESS: Repository is clean, synced, and secured!"
echo "=================================================="
