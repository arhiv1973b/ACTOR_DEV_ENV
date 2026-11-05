# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, TI-ULA

import json
import os
import re
import subprocess

FIX_LOG_PATH = "fix_log.json"


def extract_code(markdown_text):
    """Извлекает чистый код из Markdown-блоков (```python ... ```)."""
    match = re.search(
        r"```(?:python|ps1)?\n(.*?)\n```", markdown_text, re.DOTALL | re.IGNORECASE
    )
    return match.group(1).strip() if match else markdown_text.strip()


def apply_fixes():
    print("[Модуль применения] Запуск безопасного внедрения патчей...")

    if not os.path.exists(FIX_LOG_PATH):
        print(f"[ИНФО] Лог {FIX_LOG_PATH} не найден. Нет ожидающих задач.")
        return

    with open(FIX_LOG_PATH, "r", encoding="utf-8") as f:
        fixes = json.load(f)

    applied_count = 0
    for fix in fixes:
        if fix.get("status") == "pending_apply":
            incident_id = fix["incident_id"]
            print(f"\n[Анализ] Извлечение кода для инцидента {incident_id}...")

            raw_code = extract_code(fix["suggested_fix"])
            # Создаем временный скрипт для изоляции исполнения
            temp_script_name = f"auto_patch_{incident_id}.py"

            with open(temp_script_name, "w", encoding="utf-8") as temp_file:
                temp_file.write(raw_code)

            print(f"[Исполнение] Запуск сгенерированного патча {temp_script_name}...")
            try:
                subprocess.run(["python", temp_script_name], check=True)
                fix["status"] = "applied"
                print(
                    f"[УСПЕХ] Инцидент {incident_id} устранен. Статус обновлен на 'applied'."
                )
                applied_count += 1
            except subprocess.CalledProcessError as e:
                print(
                    f"[КРИТИЧЕСКАЯ ОШИБКА] Патч для {incident_id} завершился с кодом ошибки."
                )
                fix["status"] = "failed_apply"
            finally:
                # Очистка временных файлов ремонта (опционально, можно оставить для аудита)
                if os.path.exists(temp_script_name):
                    os.remove(temp_script_name)

    if applied_count > 0:
        with open(FIX_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(fixes, f, ensure_ascii=False, indent=4)
        print("\n[Модуль применения] Все изменения зафиксированы в fix_log.json.")
    else:
        print("\n[ИНФО] Нет патчей, успешно примененных в этой сессии.")


if __name__ == "__main__":
    # Создадим пустой config.yaml для теста, если его нет
    test_target = "H:\\ACTOR_DEV_ENV\\config.yaml"
    if not os.path.exists(test_target):
        with open(test_target, "w", encoding="ansi") as f:
            f.write("mock_config: test_value\n")

    apply_fixes()
