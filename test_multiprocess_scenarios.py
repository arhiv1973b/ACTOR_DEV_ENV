import os
import sys
import json
import time
import multiprocessing as mp
from audit_guard import load_audit_log_safely, append_audit_entry_safely, atomic_write_json

AUDIT_LOG = "audit_log.json"

def mp_writer_worker(idx, count=20):
    for i in range(count):
        try:
            append_audit_entry_safely({"process": idx, "op": i, "status": "OK"})
        except Exception as e:
            print(f"Writer {idx} error: {e}")

def mp_reader_worker(idx, count=20):
    for i in range(count):
        try:
            data = load_audit_log_safely(AUDIT_LOG)
            assert isinstance(data, list)
        except Exception as e:
            print(f"Reader {idx} error: {e}")

def mp_repair_worker(idx):
    try:
        data = load_audit_log_safely(AUDIT_LOG)
        assert isinstance(data, list)
    except Exception as e:
        print(f"Repair worker {idx} error: {e}")

def test_multiprocess_append():
    print("=== SCENARIO: MULTIPROCESS_APPEND (20 processes × 10 ops) ===")
    atomic_write_json(AUDIT_LOG, [])
    
    procs = []
    for i in range(20):
        p = mp.Process(target=mp_writer_worker, args=(i, 10))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    data = load_audit_log_safely(AUDIT_LOG)
    print(f"Total entries recorded: {len(data)} (Expected: 200)")
    assert len(data) == 200, f"Expected 200 entries, got {len(data)}"

    unique_ids = {(item.get("process"), item.get("op")) for item in data if "process" in item}
    print(f"Unique process/op pairs: {len(unique_ids)} (Expected: 200)")
    assert len(unique_ids) == 200, f"Expected 200 unique pairs, got {len(unique_ids)}"
    print("[SUCCESS] MULTIPROCESS_APPEND with unique ID validation passed.")

def test_multiprocess_append_heavy():
    print("=== SCENARIO: MULTIPROCESS_APPEND_HEAVY (20 processes × 50 ops = 1000 records) ===")
    atomic_write_json(AUDIT_LOG, [])

    procs = []
    for i in range(20):
        p = mp.Process(target=mp_writer_worker, args=(i, 50))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    data = load_audit_log_safely(AUDIT_LOG)
    print(f"Total heavy entries recorded: {len(data)} (Expected: 1000)")
    assert len(data) == 1000, f"Expected 1000 entries, got {len(data)}"

    unique_ids = {(item.get("process"), item.get("op")) for item in data if "process" in item}
    print(f"Unique heavy process/op pairs: {len(unique_ids)} (Expected: 1000)")
    assert len(unique_ids) == 1000, f"Expected 1000 unique pairs, got {len(unique_ids)}"
    print("[SUCCESS] MULTIPROCESS_APPEND_HEAVY passed.")

def test_multiprocess_read_write_race():
    print("=== SCENARIO: MULTIPROCESS_READ_WRITE_RACE (5 writers, 5 readers × 30 ops) ===")
    atomic_write_json(AUDIT_LOG, [])

    procs = []
    for i in range(5):
        pw = mp.Process(target=mp_writer_worker, args=(i, 30))
        pr = mp.Process(target=mp_reader_worker, args=(i, 30))
        pw.start()
        pr.start()
        procs.extend([pw, pr])

    for p in procs:
        p.join()

    data = load_audit_log_safely(AUDIT_LOG)
    print(f"Total entries after race: {len(data)} (Expected: 150)")
    assert len(data) == 150, f"Expected 150 entries, got {len(data)}"

    unique_ids = {(item.get("process"), item.get("op")) for item in data if "process" in item}
    assert len(unique_ids) == 150, f"Expected 150 unique pairs, got {len(unique_ids)}"
    print("[SUCCESS] MULTIPROCESS_READ_WRITE_RACE passed.")

def test_multiprocess_repair_race():
    print("=== SCENARIO: MULTIPROCESS_REPAIR_RACE (Corrupted Log Hit by 10 Processes) ===")
    corrupt_file = AUDIT_LOG + ".corrupt"
    if os.path.exists(corrupt_file):
        os.remove(corrupt_file)

    with open(AUDIT_LOG, "w", encoding="utf-8") as f:
        f.write("CORRUPTED_JSON_DATA_FOR_RACE_TEST{invalid}")

    procs = []
    for i in range(10):
        p = mp.Process(target=mp_repair_worker, args=(i,))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    data = load_audit_log_safely(AUDIT_LOG)
    assert isinstance(data, list), "Log must be successfully self-healed to a list"

    assert os.path.exists(corrupt_file), "Corrupt backup file must be created"
    assert os.path.getsize(corrupt_file) > 0, "Corrupt backup file must not be empty"
    assert os.path.getsize(AUDIT_LOG) > 0, "Healed audit log must not be empty"
    print(f"Backup verified: {corrupt_file} exists and size > 0.")
    print("[SUCCESS] MULTIPROCESS_REPAIR_RACE with backup verification passed.")

def locker_holder(lock_path, hold_duration):
    import portalocker
    try:
        with portalocker.Lock(lock_path, timeout=20, mode="a+", encoding="utf-8"):
            time.sleep(hold_duration)
    except Exception as e:
        print(f"Locker holder error: {e}")

def test_forced_lock_contention():
    print("=== SCENARIO: FORCED_LOCK_CONTENTION ===")
    lock_path = AUDIT_LOG + ".lock"
    
    holder_p = mp.Process(target=locker_holder, args=(lock_path, 3))
    holder_p.start()
    
    time.sleep(0.5)

    start_time = time.time()
    append_audit_entry_safely({"event": "contention_test"})
    elapsed = time.time() - start_time

    holder_p.join()

    print(f"Lock contention wait time: {elapsed:.2f}s (Expected >= 2s)")
    assert elapsed >= 1.8, f"Expected append to block for at least 1.8s, took {elapsed:.2f}s"
    print("[SUCCESS] FORCED_LOCK_CONTENTION passed.")

if __name__ == "__main__":
    mp.freeze_support()
    print("Starting Comprehensive Multi-Process Hardened Test Suite...\n")
    test_multiprocess_append()
    test_multiprocess_append_heavy()
    test_multiprocess_read_write_race()
    test_multiprocess_repair_race()
    test_forced_lock_contention()
    print("\nAll multi-process concurrency, heavy load, repair backup, and lock contention scenarios passed successfully!")
