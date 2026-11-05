#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instant PDF Indexer & SHA-256 Calculator (Incremental & High-Performance Caching)
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

A©TOR_KEY = "# [⚖ A©tor Declaration]"
BUFFER_SIZE = 131072  # 128KB


def calculate_file_sha256(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb", buffering=0) as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"ERROR: {e}"


def process_single_pdf(pdf_path, cached_entry=None):
    try:
        path_str = str(pdf_path)
        stat = pdf_path.stat()

        # Incremental caching check: if size and mtime match cache, reuse sha256
        if (
            cached_entry
            and cached_entry.get("size_bytes") == stat.st_size
            and cached_entry.get("mtime") == stat.st_mtime
        ):
            return cached_entry, True

        file_sha = calculate_file_sha256(path_str)
        return {
            "filename": pdf_path.name,
            "path": path_str,
            "size_bytes": stat.st_size,
            "sha256": file_sha,
            "mtime": stat.st_mtime,
        }, False
    except Exception as e:
        return {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "error": str(e),
        }, False


def main():
    target_root = Path(r"H:\ACTOR_DEV_ENV")
    if len(sys.argv) > 1:
        target_root = Path(sys.argv[1])
    elif Path(r"F:\Мой диск").exists():
        target_root = Path(r"F:\Мой диск")

    print(
        f"[{A©TOR_KEY}] Сканирование и инкрементальная индексация PDF в: {target_root}"
    )
    t0 = time.time()

    pdf_files = list(target_root.glob("**/*.pdf"))
    total_count = len(pdf_files)
    print(f"[{A©TOR_KEY}] Найдено PDF-файлов: {total_count}")

    if total_count == 0:
        print(f"[{A©TOR_KEY}] ❌ PDF-файлы не найдены.")
        sys.exit(0)

    # Load existing cache if present
    output_json = "instant_pdf_index.json"
    existing_index = {}
    if os.path.exists(output_json):
        try:
            with open(output_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_index = data.get("index", {})
                print(
                    f"[{A©TOR_KEY}] Загружен существующий кэш индексов ({len(existing_index)} записей)."
                )
        except Exception:
            pass

    index_data = {
        "scan_root": str(target_root),
        "total_pdf_count": total_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "index": {},
    }

    max_workers = min(32, (os.cpu_count() or 4) * 2)
    print(f"[{A©TOR_KEY}] Параллельная обработка ({max_workers} потоков)...")

    success_count = 0
    total_size = 0
    cache_hits = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for p in pdf_files:
            file_id = p.stem.upper().replace(" ", "_")
            cached = existing_index.get(file_id)
            futures[executor.submit(process_single_pdf, p, cached)] = p

        completed = 0
        for future in as_completed(futures):
            completed += 1
            res, is_cached = future.result()
            if "error" not in res:
                file_id = Path(res["filename"]).stem.upper().replace(" ", "_")
                if file_id in index_data["index"]:
                    file_id = f"{file_id}_{res['sha256'][:8]}"
                index_data["index"][file_id] = res
                success_count += 1
                total_size += res.get("size_bytes", 0)
                if is_cached:
                    cache_hits += 1

            if completed % 100 == 0 or completed == total_count:
                print(
                    f"[{A©TOR_KEY}] Обработано {completed}/{total_count} (кэш-хитов: {cache_hits})...",
                    flush=True,
                )

    elapsed = time.time() - t0
    index_data["total_size_bytes"] = total_size
    index_data["elapsed_seconds"] = round(elapsed, 3)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"[{A©TOR_KEY}] ✔ ИНДЕКС МГНОВЕННОГО ДОСТУПА ОБНОВЛЕН")
    print(f"  Всего PDF:       {success_count} / {total_count}")
    print(f"  Из кэша (быстро): {cache_hits}")
    print(f"  Суммарный объем:  {round(total_size / (1024 * 1024), 2)} MB")
    print(f"  Время выполнения: {round(elapsed, 2)} секунд")
    print(f"  Файл индекса:     {os.path.abspath(output_json)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
