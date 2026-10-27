import os
import json
import datetime
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

root_dir = r"F:\Мой диск"
out_path = Path(r"H:\ACTOR_DEV_ENV\duplication_map.json")
os.makedirs(out_path.parent, exist_ok=True)


def sha256_file(fp):
    h = hashlib.sha256()
    try:
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def process_file(fp):
    try:
        size = os.path.getsize(fp)
        return fp, size
    except Exception:
        return fp, None


def main():
    print(f"🚀 [CASE-MACHERET-1997-2026] Запуск сканирования: {root_dir}")
    size_dict = {}
    file_list = []

    # Этап 1: Рекурсивный сбор путей
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_list.append(os.path.join(root, file))

    total_files = len(file_list)
    print(f"📂 Найдено файлов: {total_files}. Параллельный анализ размеров...")

    # Многопоточный сбор размеров (ускорение для дисков F:)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, fp): fp for fp in file_list}
        for future in as_completed(futures):
            fp, s = future.result()
            if s is not None:
                size_dict.setdefault(s, []).append(fp)

    potential_dups = {s: paths for s, paths in size_dict.items() if len(paths) > 1}
    print(
        f"🔍 Найдено групп одинакового размера: {len(potential_dups)}. Проверка SHA-256..."
    )

    duplication_map = []
    wasted_bytes = 0

    # Этап 2: Проверка хэшей с оптимизацией (исключен повторный расчет для совпадений)
    for s, paths in potential_dups.items():
        hash_dict = {}
        for fp in paths:
            h = sha256_file(fp)
            if h:
                hash_dict.setdefault(h, []).append(fp)

        for h, hpaths in hash_dict.items():
            if len(hpaths) > 1:
                master = hpaths[0]
                duplicates = hpaths[1:]
                # Оптимизация: используем готовый хэш h
                file_hashes = {fp: h for fp in hpaths}
                group_wasted = s * (len(hpaths) - 1)
                wasted_bytes += group_wasted
                record = {
                    "sha256_group": file_hashes,
                    "master_file": master,
                    "duplicates": duplicates,
                    "status": "PENDING_POINTER_REPLACEMENT",
                    "size_bytes": s,
                    "wasted_bytes": group_wasted,
                    "wasted_space_mb": round(group_wasted / (1024 * 1024), 2),
                    "wasted_space_gb": round(group_wasted / (1024 * 1024 * 1024), 2),
                }
                duplication_map.append(record)

    container = {
        "case": "CASE-MACHERET-1997-2026",
        "protocol": "A©tor Jus Cogens Ledger",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_files_scanned": total_files,
        "duplication_groups": len(duplication_map),
        "duplicate_files_count": sum(len(r["duplicates"]) for r in duplication_map),
        "wasted_bytes": wasted_bytes,
        "wasted_space_mb": round(wasted_bytes / (1024 * 1024), 2),
        "wasted_space_gb": round(wasted_bytes / (1024 * 1024 * 1024), 2),
        "duplication_map": duplication_map,
    }

    out_path.write_text(
        json.dumps(container, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✅ Duplication map saved to {out_path}")
    print(
        f"📊 Всего файлов: {total_files} | Групп дублей: {len(duplication_map)} | Потеряно: {container['wasted_space_mb']} МБ"
    )


if __name__ == "__main__":
    main()
