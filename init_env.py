import os
from pathlib import Path


def initialize_workspace():
    base_dir = Path(r"H:\ACTOR_DEV_ENV")
    subdirectories = ["keys", "logs", "cache"]

    print(f"[*] Инициализация рабочей среды проекта на диске: {base_dir}")

    try:
        # Шаг 1: Создание корневой директории
        base_dir.mkdir(parents=True, exist_ok=True)
        print(f"  [+] Корневая папка проверена/создана: {base_dir}")

        # Шаг 2: Создание защищенных поддиректорий
        for sub in subdirectories:
            sub_path = base_dir / sub
            sub_path.mkdir(exist_ok=True)
            print(f"  [+] Поддиректория: {sub_path}")

        # Шаг 3: Проверка прав на запись и кодировки UTF-8
        test_file = base_dir / "permissions_test.tmp"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("A©t0r environment check: OK")
        test_file.unlink()

        print("  [+] Права записи (Write Access): УСПЕШНО")
        print("  [+] Поддержка кодировки UTF-8: УСПЕШНО")

        print("\n✅ Рабочая среда полностью готова к работе!")
        return True

    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА инициализации: {e}")
        return False


if __name__ == "__main__":
    initialize_workspace()
