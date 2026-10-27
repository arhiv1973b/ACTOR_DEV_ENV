# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

import os
import sys

print("[⚖ TI-ULA Audit Encoding] Запуск проверки кодировки UTF-8 и матрицы A©tor...")

repo_root = r"H:\ACTOR_DEV_ENV"
errors = 0
checked = 0

extensions = (".py", ".ps1", ".json", ".md", ".yml", ".yaml")

for f in os.listdir(repo_root):
    fpath = os.path.join(repo_root, f)
    if os.path.isfile(fpath) and f.lower().endswith(extensions):
        checked += 1
        try:
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
            if "A0tor" in content and f != "audit_encoding.py":
                print(f"❌ ОБНАРУЖЕН СУРРОГАТ: {fpath}")
                errors += 1
        except UnicodeDecodeError:
            print(f"❌ ОШИБКА КОДИРОВКИ: {fpath}")
            errors += 1

print(f"\nРезультаты аудита: проверено файлов: {checked}, ошибок: {errors}")
sys.exit(1 if errors > 0 else 0)
