import json
import hashlib
from pathlib import Path

LEDGER_NDJSON = "audit_log.ndjson"
CHECKPOINT_INTERVAL = 100  # Checkpoint every N blocks


def verify_ledger():
    ledger_path = Path(LEDGER_NDJSON)
    if not ledger_path.exists():
        print(f"❌ Error: Ledger file {LEDGER_NDJSON} not found.")
        return False

    lines = [
        l.strip()
        for l in ledger_path.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    print(f"=== TI-ULA / A©tor Protocol: Evidence Ledger Verification Agent ===")
    print(f"Total blocks in ledger: {len(lines)}")

    expected_prev_hash = "GENESIS_BLOCK_CASE_MACHERET_1997_2026"
    errors_count = 0
    defects_count = 0
    checkpoints = {}

    for idx, line in enumerate(lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"❌ Block #{idx}: JSON decode error: {e}")
            errors_count += 1
            continue

        block_index = record.get("index")
        prev_hash = record.get("previous_block_hash")
        stored_block_hash = record.get("block_hash")
        subject = record.get("subject", "")

        if "System Error Defect Ingestion" in subject or "error_code" in record:
            defects_count += 1

        if prev_hash != expected_prev_hash:
            print(
                f"❌ Block #{block_index or idx}: Previous hash mismatch! Expected {expected_prev_hash[:12]}..., got {str(prev_hash)[:12]}..."
            )
            errors_count += 1

        # Re-compute block hash without block_hash field
        rec_copy = dict(record)
        rec_copy.pop("block_hash", None)
        computed_hash = hashlib.sha256(
            json.dumps(rec_copy, sort_keys=True).encode("utf-8")
        ).hexdigest()

        if computed_hash != stored_block_hash:
            print(
                f"❌ Block #{block_index or idx}: Block hash mismatch! Stored {str(stored_block_hash)[:12]}..., computed {computed_hash[:12]}..."
            )
            errors_count += 1

        # Checkpoints recording
        if block_index and block_index % CHECKPOINT_INTERVAL == 0:
            checkpoints[block_index] = stored_block_hash

        expected_prev_hash = stored_block_hash

    print(f"\n--- Ledger Verification Summary ---")
    print(f"Total Verified Blocks: {len(lines)}")
    print(f"Defect / Error Blocks: {defects_count}")
    print(f"Checkpoints Established: {len(checkpoints)}")
    print(f"Validation Errors: {errors_count}")

    if errors_count > 0:
        print("❌ LEDGER INTEGRITY COMPROMISED. Strict Gate Failed.")
        return False
    else:
        print("✅ LEDGER INTEGRITY 100% VERIFIED (Jus Cogens: PASSED).")
        return True


if __name__ == "__main__":
    success = verify_ledger()
    exit(0 if success else 1)
