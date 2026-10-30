import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

root_dir = r"F:\Мой диск"
map_path = Path(r"H:\ACTOR_DEV_ENV\duplication_map.json")


def fast_hash(fp):
    hasher = hashlib.sha256()
    try:
        with open(fp, "rb") as f:
            hasher.update(f.read(65536))
        return hasher.hexdigest()
    except Exception:
        return None


def scan_root_duplicates():
    print(f"🚀 Быстрое сканирование корня {root_dir}...")
    files = [
        os.path.join(root_dir, f)
        for f in os.listdir(root_dir)
        if os.path.isfile(os.path.join(root_dir, f))
    ]

    size_dict = {}
    for fp in files:
        try:
            size = os.path.getsize(fp)
            if size > 0:
                size_dict.setdefault(size, []).append(fp)
        except Exception:
            pass

    potential_dups = {s: paths for s, paths in size_dict.items() if len(paths) > 1}
    print(
        f"🔍 Найдено групп одинакового размера в корне: {len(potential_dups)}. Проверка быстрых хэшей..."
    )

    duplication_map = []
    total_wasted_bytes = 0

    for s, paths in potential_dups.items():
        hash_dict = {}
        for fp in paths:
            h = fast_hash(fp)
            if h:
                hash_dict.setdefault(h, []).append(fp)

        for h, hpaths in hash_dict.items():
            if len(hpaths) > 1:
                master = hpaths[0]  # Мастер строго защищен
                duplicates = hpaths[1:]
                file_hashes = {fp: h for fp in hpaths}
                group_wasted = s * len(duplicates)
                total_wasted_bytes += group_wasted

                record = {
                    "sha256_group": file_hashes,
                    "master_file": master,
                    "duplicates": duplicates,
                    "status": "LOCAL_ROOT_ANALYZED",
                    "size_bytes": s,
                    "wasted_bytes": group_wasted,
                    "wasted_space_mb": round(group_wasted / (1024 * 1024), 2),
                    "wasted_space_gb": round(group_wasted / (1024 * 1024 * 1024), 2),
                }
                duplication_map.append(record)

    container = {
        "case": "CASE-MACHERET-1997-2026",
        "protocol": "A©tor Jus Cogens Ledger - Root Dedup",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_files_scanned": len(files),
        "duplication_groups": len(duplication_map),
        "duplicate_files_count": sum(len(r["duplicates"]) for r in duplication_map),
        "wasted_bytes": total_wasted_bytes,
        "wasted_space_mb": round(total_wasted_bytes / (1024 * 1024), 2),
        "wasted_space_gb": round(total_wasted_bytes / (1024 * 1024 * 1024), 2),
        "duplication_map": duplication_map,
    }

    map_path.write_text(
        json.dumps(container, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✅ Карта дубликатов сохранена в {map_path}")
    print(
        f"📊 Освобождаемое пространство: {container['wasted_space_mb']} МБ ({container['wasted_space_gb']} ГБ)"
    )
    return container


def create_local_pointers(container):
    print("🔗 Создание локальных указателей для дубликатов в корне...")
    for group in container.get("duplication_map", []):
        master = group["master_file"]
        for dup in group["duplicates"]:
            dup_path = Path(dup)
            if not dup_path.exists():
                continue

            pointer_path = dup_path.with_suffix(dup_path.suffix + ".pointer.json")
            pointer_data = {
                "master_target": master,
                "original_duplicate": dup,
                "size_bytes": group["size_bytes"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                pointer_path.write_text(
                    json.dumps(pointer_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                print(
                    f"  [+] Указатель создан: {dup_path.name} -> Мастер: {Path(master).name}"
                )
            except Exception as e:
                print(f"  [!] Ошибка создания указателя для {dup}: {e}")


if __name__ == "__main__":
    container = scan_root_duplicates()
    create_local_pointers(container)
