import os
import json
from pathlib import Path


def main():
    root_dir = Path(r"F:\Мой диск")
    env_dir = Path(r"H:\ACTOR_DEV_ENV")
    map_path = env_dir / "duplication_map.json"
    pointers_dir = env_dir / "pointers"
    pointers_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Генерация карты дубликатов (экспресс-режим)...")
    size_dict = {}
    try:
        for f in os.listdir(root_dir):
            fp = os.path.join(root_dir, f)
            if os.path.isfile(fp):
                try:
                    s = os.path.getsize(fp)
                    if (
                        0 < s < 50 * 1024 * 1024
                    ):  # Исключаем файлы > 50МБ для мгновенной работы
                        size_dict.setdefault(s, []).append(fp)
                except:
                    pass
    except Exception as e:
        print(f"Error listing: {e}")

    potential_dups = {s: paths for s, paths in size_dict.items() if len(paths) > 1}
    duplication_map = []
    total_wasted = 0

    for s, paths in potential_dups.items():
        master = paths[0]  # Мастер строго защищен
        duplicates = paths[1:]
        wasted = s * len(duplicates)
        total_wasted += wasted
        record = {
            "master_file": master,
            "duplicates": duplicates,
            "size_bytes": s,
            "wasted_bytes": wasted,
            "wasted_space_mb": round(wasted / (1024 * 1024), 2),
            "status": "POINTER_RESOLVED",
        }
        duplication_map.append(record)

    container = {
        "case": "CASE-MACHERET-1997-2026",
        "total_groups": len(duplication_map),
        "wasted_bytes": total_wasted,
        "wasted_space_mb": round(total_wasted / (1024 * 1024), 2),
        "duplication_map": duplication_map,
    }

    map_path.write_text(
        json.dumps(container, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"✅ Карта сохранена: {map_path} (Потеряно: {container['wasted_space_mb']} МБ)"
    )

    print("🔗 Создание локальных указателей...")
    count = 0
    for group in duplication_map:
        master = group["master_file"]
        for dup in group["duplicates"]:
            dup_name = Path(dup).name
            pointer_path = pointers_dir / f"{dup_name}.pointer.json"
            pointer_data = {
                "master_target": master,
                "original_duplicate": dup,
                "size_bytes": group["size_bytes"],
            }
            pointer_path.write_text(
                json.dumps(pointer_data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            count += 1

    print(f"✅ Создано указателей: {count} в {pointers_dir}")

    # Верификация
    pointers = list(pointers_dir.glob("*.pointer.json"))
    print(f"🔍 Верификация: найдено файлов-указателей: {len(pointers)}")
    for i, p in enumerate(pointers[:5], 1):
        data = json.loads(p.read_text(encoding="utf-8"))
        print(f"  [{i}] {p.name} -> Мастер: {Path(data['master_target']).name}")


if __name__ == "__main__":
    main()
