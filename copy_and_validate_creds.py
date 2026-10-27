import os
import json
from pathlib import Path
import shutil

# Пути к источнику и целевой локальной папке на диске H:
source_path = Path(
    r"C:\Users\arhiv\AppData\Local\google-vscode-extension\auth\credentials.json"
)
target_dir = Path(r"H:\ACTOR_DEV_ENV")
target_path = target_dir / "credentials.json"


def validate_and_copy():
    print(f"🔄 Проверка источника: {source_path}")
    if not source_path.exists():
        print(f"❌ ОШИБКА: Исходный файл не найден по пути {source_path}")
        return False

    # Шаг 1: Валидация структуры JSON
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ОШИБКА: Файл не является валидным JSON: {e}")
        return False

    # Проверка формата: Service Account или OAuth2 (installed/web)
    if data.get("type") == "service_account":
        required_fields = ["client_email", "private_key", "client_id", "project_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"❌ ОШИБКА: В Service Account отсутствуют поля: {missing_fields}")
            return False
        print(
            f"✅ Структура JSON валидна! Тип: Service Account\n"
            f"   Email: {data.get('client_email')}\n"
            f"   Project ID: {data.get('project_id')}"
        )
    elif "installed" in data or "web" in data:
        client_type = "installed" if "installed" in data else "web"
        client_data = data[client_type]
        required_fields = ["client_id", "client_secret", "redirect_uris"]
        missing_fields = [
            field for field in required_fields if field not in client_data
        ]
        if missing_fields:
            print(
                f"❌ ОШИБКА: В структуре OAuth2 ({client_type}) отсутствуют поля: {missing_fields}"
            )
            return False
        print(
            f"✅ Структура JSON валидна! Тип клиента: '{client_type}'. Все обязательные поля на месте."
        )
    else:
        print(
            "❌ ОШИБКА: Неизвестный формат ключа (ожидался service_account, installed или web)."
        )
        return False

    # Шаг 2: Копирование на локальный диск H:
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy2(source_path, target_path)
    print(f"✅ Успешно скопировано в локальную среду: {target_path}")
    return True


if __name__ == "__main__":
    validate_and_copy()
