import os
import hashlib
import json
from datetime import datetime, timezone

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"

def generate_manifest(target_dir):
    manifest = {
        "ti_ula_header": {
            "architecture": "Transcendent Integrity - Universal Legal Architecture",
            "author": "A©tor",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "root_directory": os.path.abspath(target_dir),
            "signatures": {
                "ed25519_pubkey": None,
                "ed25519_signature": None
            }
        },
        "payload": {
            "files": []
        }
    }

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.startswith('.'):
                continue
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, target_dir)
            try:
                stat = os.stat(filepath)
                file_info = {
                    "path": rel_path,
                    "sha256": calculate_sha256(filepath),
                    "size_bytes": stat.st_size,
                    "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                }
                manifest["payload"]["files"].append(file_info)
                print(f"[OK] {rel_path} -> {file_info['sha256'][:8]}...")
            except PermissionError:
                print(f"[ACCESS DENIED] Пропуск файла: {rel_path}")
                manifest["payload"]["files"].append({
                    "path": rel_path,
                    "error": "Permission denied"
                })
            except Exception as e:
                print(f"[ERROR] {rel_path}: {e}")
    manifest_path = os.path.join(target_dir, "evidence_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"\nАудит завершен. Манифест успешно создан: {manifest_path}")

if __name__ == "__main__":
    print("Инициализация криптографического аудита TI-ULA...")
    target = "."
    generate_manifest(target)
