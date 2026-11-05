# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, TI-ULA

import os
import sys
import json

# Динамический импорт функции коммутатора из github_ai_tunnel
try:
    from github_ai_tunnel import query_copilot_socket as query_llm
except ImportError:
    try:
        from github_ai_tunnel import query_github_socket as query_llm
    except ImportError:
        print(
            "[КРИТИЧЕСКАЯ ОШИБКА] Не удалось импортировать интерфейс ИИ-туннеля из github_ai_tunnel.py"
        )
        sys.exit(1)

AUDIT_LOG_PATH = "audit_log.json"
FIX_LOG_PATH = "fix_log.json"


def analyze_and_repair():
    print("[Диспетчер Ремонта] Запуск автоматического анализа логов...")

    if not os.path.exists(AUDIT_LOG_PATH):
        print(f"[ИНФО] Лог {AUDIT_LOG_PATH} не найден. Нет задач для ремонта.")
        return

    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        try:
            audit_data = json.load(f)
        except json.JSONDecodeError:
            print(
                f"[КРИТИЧЕСКАЯ ОШИБКА] Файл {AUDIT_LOG_PATH} поврежден или имеет неверный формат."
            )
            return

    # Извлечение инцидентов со статусом error или critical
    errors = [
        item
        for item in audit_data
        if item.get("status") in ("error", "failed")
        or item.get("severity") == "critical"
    ]

    if not errors:
        print(
            "[ИНФО] Критичных инцидентов для ремонта не обнаружено. Система стабильна."
        )
        return

    print(
        f"[Диспетчер Ремонта] Найдено {len(errors)} инцидентов. Инициализация ИИ-коммутатора..."
    )

    fixes = []
    for error in errors:
        error_id = error.get("id", error.get("module", "unknown"))

        prompt = (
            f"Проанализируй следующую системную ошибку и предложи скрипт (Python/PowerShell) для её устранения.\n"
            f"Контекст: TI-ULA, строгий UTF-8, песочница Windows.\n"
            f"Инцидент: {json.dumps(error, ensure_ascii=False, indent=2)}\n"
            f"Верни ТОЛЬКО исполняемый код исправления, без текстовых пояснений."
        )

        print(
            f"[Диспетчер Ремонта] Маршрутизация инцидента {error_id} через ИИ-туннель..."
        )
        ai_response = query_llm(prompt)

        if ai_response:
            fixes.append(
                {
                    "incident_id": error_id,
                    "suggested_fix": ai_response,
                    "status": "pending_apply",
                }
            )
            print(f"[УСПЕХ] Патч для инцидента {error_id} сгенерирован.")
        else:
            print(f"[СБОЙ] Не удалось получить решение для {error_id}.")

    if fixes:
        # Запись предложенных исправлений в лог с соблюдением кодировки
        with open(FIX_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(fixes, f, ensure_ascii=False, indent=4)
        print(
            f"[Диспетчер Ремонта] Все предложенные ИИ патчи сохранены в {FIX_LOG_PATH}."
        )


if __name__ == "__main__":
    analyze_and_repair()
