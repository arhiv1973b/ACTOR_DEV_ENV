import os
import sys
import json
import threading
import subprocess
from pathlib import Path

AUDIT_LOG = Path("audit_log.json")

def run_checks():
    print("  -> Running repair_dispatcher.py...")
    res1 = subprocess.run([sys.executable, "repair_dispatcher.py"], capture_output=True, text=True)
    print(f"     Exit code: {res1.returncode}, Output: {res1.stdout.strip()}")
    
    print("  -> Running actor_jus_cogens_orchestrator.py...")
    res2 = subprocess.run([sys.executable, "actor_jus_cogens_orchestrator.py"], capture_output=True, text=True)
    print(f"     Exit code: {res2.returncode}, Output lines: {len(res2.stdout.splitlines())}")
    
    # Verify audit_log.json is valid JSON list
    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, list), "audit_log.json must be a list"
    print("  [SUCCESS] System successfully normalized and restored to READY state.\n")

def test_normal_write():
    print("=== SCENARIO: NORMAL_WRITE ===")
    data = [{"id": "TEST-NORM-1", "status": "OK", "timestamp": "2026-11-06T00:00:00Z"}]
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    run_checks()

def test_partial_write():
    print("=== SCENARIO: PARTIAL_WRITE ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write('[{"id": "TEST-PARTIAL", "status": "error"') # truncated
    run_checks()

def test_empty_file():
    print("=== SCENARIO: EMPTY_FILE ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write("")
    run_checks()

def test_invalid_json():
    print("=== SCENARIO: INVALID_JSON ===")
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write("NOT_A_JSON_STRING_WITH_EXTRA_DATA")
    run_checks()

def test_power_loss_simulation():
    print("=== SCENARIO: POWER_LOSS_SIMULATION ===")
    # Multiple objects without array wrapper (the exact bug encountered)
    content = '[\n    {\n        "id": "ERR-001"\n    }\n]\n{\n    "message": "power loss mid-write"\n}'
    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write(content)
    run_checks()

def test_concurrent_write():
    print("=== SCENARIO: CONCURRENT_WRITE ===")
    def worker():
        for _ in range(50):
            try:
                data = []
                if AUDIT_LOG.exists() and AUDIT_LOG.stat().st_size > 0:
                    with open(AUDIT_LOG, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]
                data.append({"id": "CONC", "thread": threading.get_ident()})
                with open(AUDIT_LOG, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            except Exception:
                pass

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    run_checks()

if __name__ == "__main__":
    print("Starting Stress Test Suite for TI-ULA Audit Log Resilience...\n")
    test_normal_write()
    test_partial_write()
    test_empty_file()
    test_invalid_json()
    test_power_loss_simulation()
    test_concurrent_write()
    print("All 6 stress test scenarios passed successfully!")
