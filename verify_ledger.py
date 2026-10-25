import json
import hashlib
import datetime
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

    stats = {
        "evidence_blocks": 0,
        "error_defect_blocks": 0,
        "tsa_audit_blocks": 0,
        "git_commit_blocks": 0,
        "other_blocks": 0,
    }

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
            stats["error_defect_blocks"] += 1
        elif "Evidence Ingestion" in subject or "evidence_file" in record:
            stats["evidence_blocks"] += 1
        elif "TSA Health Audit" in subject or "metrics" in record:
            stats["tsa_audit_blocks"] += 1
        elif "commit" in record or "subject" in record:
            stats["git_commit_blocks"] += 1
        else:
            stats["other_blocks"] += 1

        if prev_hash != expected_prev_hash:
            print(
                f"❌ Block #{block_index or idx}: Previous hash mismatch! Expected {expected_prev_hash[:12]}..., got {str(prev_hash)[:12]}..."
            )
            errors_count += 1

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

        if block_index and block_index % CHECKPOINT_INTERVAL == 0:
            checkpoints[block_index] = stored_block_hash

        expected_prev_hash = stored_block_hash

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    status_badge = "PASSED ✅" if errors_count == 0 else "COMPROMISED ❌"

    total_lines = len(lines) if len(lines) > 0 else 1

    dashboard_content = f"""# 🛡️ A©tor Integrity Dashboard & Ledger Audit Report

- **Timestamp (UTC)**: {timestamp}
- **Ledger Status**: {status_badge}
- **Total Blocks Verified**: {len(lines)}
- **Validation Errors**: {errors_count}

## 📊 Block Type Statistics
| Block Category | Count | Percentage |
|:---|:---|:---|
| 📂 Evidence Ingestion Blocks | {stats["evidence_blocks"]} | {stats["evidence_blocks"] / total_lines * 100:.2f}% |
| ❌ System Error / Defect Blocks | {stats["error_defect_blocks"]} | {stats["error_defect_blocks"] / total_lines * 100:.2f}% |
| 📡 TSA Health Audit Blocks | {stats["tsa_audit_blocks"]} | {stats["tsa_audit_blocks"] / total_lines * 100:.2f}% |
| 📜 Git Commit & Standard Blocks | {stats["git_commit_blocks"]} | {stats["git_commit_blocks"] / total_lines * 100:.2f}% |
| 📦 Other / Unclassified | {stats["other_blocks"]} | {stats["other_blocks"] / total_lines * 100:.2f}% |

## 🔐 Cryptographic Checkpoints (Every {CHECKPOINT_INTERVAL} Blocks)
| Block Index | Checkpoint Block Hash (SHA-256) |
|:---|:---|
"""
    for cp_idx, cp_hash in sorted(checkpoints.items()):
        dashboard_content += f"| #{cp_idx} | `{cp_hash}` |\n"

    dashboard_content += f"""
---
*Generated automatically by A©tor Integrity Verification Agent under Jus Cogens & Erga Omnes protocols.*
"""

    Path("integrity_dashboard.md").write_text(dashboard_content, encoding="utf-8")
    print("✅ integrity_dashboard.md successfully generated.")

    print(f"\n--- Ledger Verification Summary ---")
    print(f"Total Verified Blocks: {len(lines)}")
    print(f"Evidence Blocks: {stats['evidence_blocks']}")
    print(f"Error / Defect Blocks: {stats['error_defect_blocks']}")
    print(f"TSA Audit Blocks: {stats['tsa_audit_blocks']}")
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
