# A©TOR_KEY="# [⚖ A©tor Declaration]"
# Legal Scope: Erga Omnes, TI-ULA - Audit Log Self-Healing, Atomic & Multi-Process Safe Guard

import json
import os
import tempfile
import threading
import time
import portalocker

LOG_FILE = "audit_log.json"
_thread_lock = threading.Lock()


def atomic_write_json(path, data, use_lock=False):
    """
    Atomically writes JSON data to disk using a temporary file in the same directory,
    fsync flushing, and os.replace to prevent partial writes and power-loss corruption.
    """
    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    def _write():
        fd, tmp = tempfile.mkstemp(dir=directory if directory else ".", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass

    if use_lock:
        lock_path = str(path) + ".lock"
        with portalocker.Lock(lock_path, timeout=10, check_interval=0.05):
            _write()
    else:
        _write()


def load_audit_log_safely(log_path=LOG_FILE, repair_callback=None):
    """
    Safely loads audit_log.json with automatic fallback recovery on corruption
    or decoding errors, protected by thread lock and portalocker multi-process file lock with retries.
    """
    with _thread_lock:
        lock_path = str(log_path) + ".lock"
        for attempt in range(60):
            try:
                with portalocker.Lock(lock_path, timeout=10, check_interval=0.05):
                    try:
                        if (
                            not os.path.exists(log_path)
                            or os.path.getsize(log_path) == 0
                        ):
                            return []
                        with open(log_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if not isinstance(data, list):
                                data = [data]
                        return data
                    except Exception as e:
                        print(
                            f"[AUDIT GUARD] Warning: Corrupted log detected ({e}). Initiating self-repair..."
                        )
                        if repair_callback:
                            try:
                                repair_callback()
                            except Exception as rc_err:
                                print(f"[AUDIT GUARD] Repair callback failed: {rc_err}")

                        if os.path.exists(log_path):
                            try:
                                corrupt_backup = str(log_path) + ".corrupt"
                                if os.path.exists(corrupt_backup):
                                    os.remove(corrupt_backup)
                                os.rename(log_path, corrupt_backup)
                            except Exception:
                                pass

                        atomic_write_json(log_path, [])
                        print(f"[AUDIT GUARD] Log successfully reset to clean state.")

                        with open(log_path, "r", encoding="utf-8") as f:
                            return json.load(f)
            except (portalocker.LockException, PermissionError, OSError):
                if attempt == 59:
                    raise
                time.sleep(0.05 + (attempt * 0.01))


def append_audit_entry_safely(entry, log_path=LOG_FILE):
    """
    Safely appends a new audit entry with thread-safe locking, portalocker multi-process locking
    with Windows-compatible permission retries, and atomic write guarantees.
    """
    with _thread_lock:
        lock_path = str(log_path) + ".lock"
        for attempt in range(60):
            try:
                with portalocker.Lock(lock_path, timeout=10, check_interval=0.05):
                    data = []
                    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
                        try:
                            with open(log_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if not isinstance(data, list):
                                    data = [data]
                        except Exception:
                            data = []
                    data.append(entry)
                    atomic_write_json(log_path, data)
                    return
            except (portalocker.LockException, PermissionError, OSError):
                if attempt == 59:
                    raise
                time.sleep(0.05 + (attempt * 0.01))
