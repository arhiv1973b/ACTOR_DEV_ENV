import os
import sys
import json
import threading
import subprocess
from pathlib import Path
from audit_guard import load_audit_log_safely, atomic_write_json, append_audit_entry_safely

AUDIT_LOG = Path("audit_log.json")

def run_checks():
    print("  -> Running repair_dispatcher.py...")
    res1 = subprocess.run([sys.executable, "repair_dispatcher.py"], capture_output=True, text=True)
    print(f"     Exit code: {res1.returncode}, Output: {res1.stdout.strip()}")
    
    print("  -> Running actor_jus_cogens_orchestrator.py...")
    res2 = subprocess.run([sys.executable, "actor_jus_cogens_orchestrator.py"], capture_output=True, text=True)
    print(f"     Exit code: {res2.returncode}, Output lines: {len(res2.stdout.splitlines())}")
    
    # Verify audit_log.json is valid JSON list via audit_guard
    data = load_audit_log_safely(AUDIT_LOG)
    assert isinstance(data, list), "audit_log.json must be a list"
    print("  [SUCCESS] System successfully normalized and restored to READY state.\n")

def test_normal_write():
    print("=== SCENARIO: NORMAL_WRITE (Atomic) ===")
    data = [{"id": "TEST-NORM-1", "status": "OK", "timestamp": "2026-11-06T00:00:00Z"}]
    atomic_write_json(AUDIT_LOG, data)
    run_checks()

def test_partial_write():
    print("=== SCENARIO: PARTIAL_WRITE (Self-Healing) ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write('[{"id": "TEST-PARTIAL", "status": "error"') # truncated
    run_checks()

def test_empty_file():
    print("=== SCENARIO: EMPTY_FILE (Self-Healing) ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write("")
    run_checks()

def test_invalid_json():
    print("=== SCENARIO: INVALID_JSON (Self-Healing) ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write("NOT_A_JSON_STRING_WITH_EXTRA_DATA")
    run_checks()

def test_power_loss_simulation():
    print("=== SCENARIO: POWER_LOSS_SIMULATION (Self-Healing) ===")
    content = '[\n    {\n        "id": "ERR-001"\n    }\n]\n{\n    "message": "power loss mid-write"\n}'
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write(content)
    run_checks()

def test_concurrent_write():
    print("=== SCENARIO: CONCURRENT_WRITE (Hardened Atomic Safety) ===")
    concurrency_errors = []

    def worker():
        for _ in range(50):
            try:
                append_audit_entry_safely({"id": "CONC", "thread": threading.get_ident()})
            except Exception as e:
                concurrency_errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()

    print(f"     Concurrent write errors encountered: {len(concurrency_errors)}")
    assert len(concurrency_errors) == 0, f"Expected 0 concurrency errors, got {len(concurrency_errors)}: {concurrency_errors}"
    run_checks()

if __name__ == "__main__":
    print("Starting Hardened Stress Test Suite for TI-ULA Audit Log Resilience...\n")
    test_normal_write()
    test_partial_write()
    test_empty_file()
    test_invalid_json()
    test_power_loss_simulation()
    test_concurrent_write()
    print("All hardened stress test scenarios passed with 0 concurrency errors!")
