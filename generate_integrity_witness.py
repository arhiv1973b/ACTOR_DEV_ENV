# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, ВДПЧ 1948, TI-ULA

import os
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_DIR = r"H:\ACTOR_DEV_ENV"
LOGS_DIR = os.path.join(WORKSPACE_DIR, "secure_logs")
MANIFEST_FILE = os.path.join(WORKSPACE_DIR, "INTEGRITY_WITNESS.json")


def compute_sha256(file_path):
    """Вычисляет SHA-256 для файла потоковым методом."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


def build_merkle_root(hash_list):
    """Вычисляет детерминированный Merkle root из списка хэшей."""
    if not hash_list:
        return None
    # Сортировка обязательна для иммутабельной последовательности
    sorted_hashes = sorted(hash_list)
    combined = "".join(sorted_hashes).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def update_integrity_witness():
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] A©t0r: Инициализация генерации Merkle root для доказательной базы."
    )

    log_files_metadata = []
    hashes_for_merkle = []

    if os.path.exists(LOGS_DIR):
        for filename in os.listdir(LOGS_DIR):
            if filename.endswith(".log") or filename.endswith(".sig"):
                filepath = os.path.join(LOGS_DIR, filename)
                file_hash = compute_sha256(filepath)
                if file_hash:
                    log_files_metadata.append(
                        {
                            "filename": filename,
                            "sha256": file_hash,
                            "timestamp": datetime.fromtimestamp(
                                os.path.getmtime(filepath), timezone.utc
                            ).isoformat(),
                        }
                    )
                    hashes_for_merkle.append(file_hash)

    merkle_root = build_merkle_root(hashes_for_merkle)

    # Структура обновления манифеста
    witness_update = {
        "actor_identity": "A©t0r (arhiv1973b)",
        "legal_scope": "Erga Omnes, ВДПЧ 1948",
        "last_verification_utc": datetime.now(timezone.utc).isoformat(),
        "secure_logs_merkle_root": merkle_root,
        "audit_files": log_files_metadata,
    }

    # Безопасное слияние с существующим манифестом, чтобы не затереть другие узлы (например, графы файлов)
    if os.path.exists(MANIFEST_FILE):
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
            manifest_data.update(witness_update)
        except Exception:
            manifest_data = witness_update
    else:
        manifest_data = witness_update

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4, ensure_ascii=False)

    print(
        f"[{datetime.now(timezone.utc).isoformat()}] INTEGRITY_WITNESS.json алгоритмически запечатан."
    )
    print(f"Merkle Root (secure_logs): {merkle_root}")


if __name__ == "__main__":
    update_integrity_witness()
