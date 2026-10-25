import json
from pathlib import Path

map_path = Path("duplication_map.json")

if map_path.exists():
    data = json.loads(map_path.read_text(encoding="utf-8"))
    print("=== СВОДНАЯ СТАТИСТИКА ДЕЛИКАТНОГО АУДИТА ===")
    print(f"📂 Всего просканировано файлов: {data.get('total_files_scanned')}")
    print(f"🔍 Найдено групп дубликатов: {data.get('duplication_groups')}")
    print(f"📄 Избыточных файлов: {data.get('duplicate_files_count')}")
    print(
        f"💾 Общий объем избыточных данных: {data.get('wasted_space_mb')} МБ ({data.get('wasted_space_gb')} ГБ)"
    )

    groups = data.get("duplication_map", [])
    if groups:
        print("\n--- Пример первой группы ---")
        g = groups[0]
        print(f"Master: {g.get('master_file')}")
        print(f"Duplicates: {g.get('duplicates')}")
        print(f"Status: {g.get('status')}")
else:
    print(
        "❌ Файл duplication_map.json пока не найден. Убедитесь, что скрипт завершил работу."
    )
