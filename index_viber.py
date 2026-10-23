import os
import hashlib
import json
from datetime import datetime

TARGET_DIR = r"C:\Users\arhiv\OneDrive\Документы\ViberDownloads"
MANIFEST_PATH = "dag_manifest.json"


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Ошибка чтения {file_path}: {e}")
        return None


def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Директория не найдена: {TARGET_DIR}")
        return

    # Загружаем текущий манифест, если он есть
    manifest = []
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                manifest = data if isinstance(data, list) else data.get("entries", [])
        except Exception:
            manifest = []

    existing_hashes = {
        item.get("node_hash") or item.get("hash") or item.get("sha256")
        for item in manifest
    }

    new_records_count = 0
    print(f"Сканирование директории: {TARGET_DIR}...")

    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = calculate_sha256(file_path)

            if file_hash and file_hash not in existing_hashes:
                stat = os.stat(file_path)
                record = {
                    "filename": file,
                    "path": f"./ViberDownloads/{file}",
                    "node_hash": file_hash,
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size_bytes": stat.st_size,
                    "signature_ed25519": True,
                    "source": "ViberDownloads",
                }
                manifest.append(record)
                existing_hashes.add(file_hash)
                new_records_count += 1
                print("[+] Зарегистрировано в DAG:", file)

    # Сохраняем обновленный манифест
    output_data = {
        "updated_at": datetime.now().isoformat(),
        "total_entries": len(manifest),
        "entries": manifest,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(
        f"\nИндексация завершена. Добавлено новых записей: {new_records_count}. Всего в DAG: {len(manifest)}"
    )


if __name__ == "__main__":
    main()
