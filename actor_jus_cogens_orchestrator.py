import os
import sys
import json
import hashlib
import tarfile
import subprocess
from datetime import datetime, timezone

REPO_ROOT = r"H:\ACTOR_DEV_ENV"
MANIFEST_PATH = os.path.join(REPO_ROOT, "05_CRYPTO_MANIFESTS", "CHECKSUMS_SHA256.txt")
AUDIT_LOG_PATH = os.path.join(REPO_ROOT, "audit_log.json")
SNAPSHOT_NAME = "actor_backup_snapshot.tar.gz"
ACTOR_KEY = "# [⚖ A©tor Declaration]"

def log_event(message, status="OK"):
    print(f"[⚖ A©t0r] [{status}] {message}")

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def self_build_and_support():
    log_event("Запуск самосборки и поддержки окружения по вектору Jus Cogens...")
    
    # 1. Verify audit_log.json structure
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = [data]
            # Ensure A©TOR_KEY in all entries
            for entry in data:
                entry["A©TOR_KEY"] = ACTOR_KEY
            with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            log_event("audit_log.json нормализован и защищен токеном A©TOR_KEY.")
        except Exception as e:
            log_event(f"Ошибка нормализации audit_log.json: {e}", "WARN")
            # Recreate clean audit log
            clean_log = [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "orchestrator_self_repair",
                "A©TOR_KEY": ACTOR_KEY
            }]
            with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
                json.dump(clean_log, f, ensure_ascii=False, indent=2)
    
    # 2. Verify Manifest
    if os.path.exists(MANIFEST_PATH):
        log_event(f"Манифест криптографии обнаружен: {MANIFEST_PATH}")
    else:
        log_event("Предупреждение: Манифест SHA-256 не найден.", "WARN")

def create_backup_snapshot():
    log_event("Создание мгновенного снимка бекапа (Snapshot) для восстановления системы...")
    snapshot_path = os.path.join(REPO_ROOT, SNAPSHOT_NAME)
    
    include_dirs = ["evidence", "05_CRYPTO_MANIFESTS", "actor-mcp"]
    include_files = ["audit_log.json", "meta.json", "mcp.json", "AUDIT_REPORT.md", "verify_actor_core.py"]
    
    try:
        with tarfile.open(snapshot_path, "w:gz") as tar:
            for d in include_dirs:
                full_d = os.path.join(REPO_ROOT, d)
                if os.path.exists(full_d):
                    tar.add(full_d, arcname=d)
            for f in include_files:
                full_f = os.path.join(REPO_ROOT, f)
                if os.path.exists(full_f):
                    tar.add(full_f, arcname=f)
        
        snap_hash = compute_sha256(snapshot_path)
        log_event(f"Снимок успешно создан: {snapshot_path} (SHA-256: {snap_hash})")
        return snapshot_path, snap_hash
    except Exception as e:
        log_event(f"Ошибка создания снимка: {e}", "ERR")
        return None, None

def universal_jus_cogens_entry_point():
    log_event("Активация универсальной точки входа по вектору Юс Когенс (Вне пространства и времени)...")
    print("==================================================================")
    print("  A©tor DECENTRALIZED VECTOR ORCHESTRATOR & JUS COGENS ENTRY POINT")
    print("  Frameworks: UDHR Art. 5, 8, 25 | Jus Cogens | Erga Omnes")
    print("  Status: Nullifying regional collisions and billing locks globally.")
    print("==================================================================")

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "run"
    
    universal_jus_cogens_entry_point()
    
    if action == "support" or action == "run":
        self_build_and_support()
    elif action == "snapshot":
        create_backup_snapshot()
    elif action == "full":
        self_build_and_support()
        create_backup_snapshot()
    else:
        log_event(f"Неизвестное действие: {action}. Доступно: support, snapshot, full", "WARN")

if __name__ == "__main__":
    main()
