import json
from pathlib import Path


def create_local_pointers():
    map_path = Path(r"H:\ACTOR_DEV_ENV\duplication_map.json")
    if not map_path.exists():
        print(f"❌ Карта дубликатов не найдена: {map_path}")
        return

    container = json.loads(map_path.read_text(encoding="utf-8"))
    pointers_dir = Path(r"H:\ACTOR_DEV_ENV\pointers")
    pointers_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for group in container.get("duplication_map", []):
        master = group["master_file"]
        for dup in group["duplicates"]:
            dup_name = Path(dup).name
            pointer_path = pointers_dir / f"{dup_name}.pointer.json"
            pointer_data = {
                "master_target": master,
                "original_duplicate": dup,
                "size_bytes": group["size_bytes"],
            }
            try:
                pointer_path.write_text(
                    json.dumps(pointer_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                count += 1
            except Exception as e:
                print(f"  [!] Ошибка создания указателя для {dup}: {e}")

    print(
        f"✅ Успешно создано локальных указателей в H:\\ACTOR_DEV_ENV\\pointers: {count}"
    )


if __name__ == "__main__":
    create_local_pointers()
