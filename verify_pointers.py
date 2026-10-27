import json
from pathlib import Path


def verify_pointers():
    pointers_dir = Path(r"H:\ACTOR_DEV_ENV\pointers")
    pointers = list(pointers_dir.glob("*.pointer.json"))

    print(f"🔍 Найдено локальных файлов-указателей: {len(pointers)}")
    print("=" * 70)

    success_count = 0
    for i, p in enumerate(pointers, 1):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            master_name = Path(data.get("master_target", "UNKNOWN")).name
            dup_name = Path(data.get("original_duplicate", "UNKNOWN")).name

            print(f"[{i:02d}] {p.name}")
            print(f"     🔗 Указывает на мастер: {master_name}")
            success_count += 1
        except Exception as e:
            print(f"[{i:02d}] ❌ Ошибка чтения {p.name}: {e}")

    print("=" * 70)
    print(f"✅ Успешно прочитано и проверено: {success_count} из {len(pointers)}")


if __name__ == "__main__":
    verify_pointers()
