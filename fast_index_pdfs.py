#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Targeted Lightning-Fast PDF Indexer (Evidence Vault & Dossier Focus)
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
INDEX_FILE = "instant_pdf_index.json"

TARGET_FOLDERS = [
    r"H:\ACTOR_DEV_ENV",
]


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


def main():
    print(f"[{A©TOR_KEY}] Целевое сканирование ключевых PDF-хранилищ...")
    t0 = time.time()

    root = Path(r"H:\ACTOR_DEV_ENV")
    # Gather PDFs from root and main evidence folders to avoid massive traversal stalls
    pdf_files = []

    # Fast glob or explicit folder collection
    subfolders = [
        "",
        "MASTER_DOSSIER",
        "Apostilles",
        "evidence-vault",
        "recovered_evidence",
        "apostille-archive-english",
        "apostille-mirror",
    ]
    for sf in subfolders:
        d = root / sf if sf else root
        if d.exists() and d.is_dir():
            try:
                for p in d.glob("*.pdf"):
                    if p not in pdf_files:
                        pdf_files.append(p)
                # Level 1 subfolders
                for sub in d.iterdir():
                    if sub.is_dir() and sub.name not in [
                        ".git",
                        ".venv_test",
                        "node_modules",
                        "tools",
                    ]:
                        for p in sub.glob("*.pdf"):
                            if p not in pdf_files:
                                pdf_files.append(p)
            except Exception:
                pass

    total_count = len(pdf_files)
    print(f"[{A©TOR_KEY}] Отобрано ключевых PDF-файлов: {total_count}")

    index_data = {
        "scan_root": str(root),
        "total_pdf_count": total_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "index": {},
    }

    def process_pdf(pdf_path):
        try:
            path_str = str(pdf_path)
            stat = pdf_path.stat()
            file_sha = calculate_file_sha256(path_str)
            return {
                "filename": pdf_path.name,
                "path": path_str,
                "size_bytes": stat.st_size,
                "sha256": file_sha,
                "mtime": stat.st_mtime,
            }
        except Exception as e:
            return {"filename": pdf_path.name, "path": str(pdf_path), "error": str(e)}

    max_workers = min(32, (os.cpu_count() or 4) * 2)
    success_count = 0
    total_size = 0

    print(f"[{A©TOR_KEY}] Параллельный расчет SHA-256 хэшей ({max_workers} потоков)...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_pdf, p): p for p in pdf_files}
        for future in as_completed(futures):
            res = future.result()
            if "error" not in res:
                file_id = Path(res["filename"]).stem.upper().replace(" ", "_")
                if file_id in index_data["index"]:
                    file_id = f"{file_id}_{res['sha256'][:8]}"
                index_data["index"][file_id] = res
                success_count += 1
                total_size += res.get("size_bytes", 0)

    elapsed = time.time() - t0
    index_data["total_size_bytes"] = total_size
    index_data["elapsed_seconds"] = round(elapsed, 3)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"[{A©TOR_KEY}] ✔ ИНДЕКС МГНОВЕННОГО ДОСТУПА СОЗДАН (ЦЕЛЕВОЙ)")
    print(f"  Проиндексировано PDF: {success_count} / {total_count}")
    print(f"  Суммарный объем:     {round(total_size / (1024 * 1024), 2)} MB")
    print(f"  Затрачено времени:   {round(elapsed, 2)} сек")
    print(f"  Файл индекса:        {os.path.abspath(INDEX_FILE)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
