import hashlib
import json
import os
import datetime
import subprocess

LEDGER_PATH = "Evidence_Ledger.json"


def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def update_ledger():
    print("=== TI-ULA / A©tor Protocol: Evidence Ledger Synchronizer ===")

    # Core artifacts to track in ledger
    tracked_files = [
        "Bloom_Exports_Manifest.md",
        "External_Verification_Report.md",
        "DeliveryStatus_PointDiff_Log.md",
        "MASTER_RECIPIENTS_REGISTRY_RM_2026.md",
        "TI_ULA_EVIDENCE_PACKAGE_DISPATCH_2026.md",
    ]

    current_artifacts = {}
    for f in tracked_files:
        h = compute_sha256(f)
        if h:
            current_artifacts[f] = h

    # Load existing ledger
    ledger = []
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r", encoding="utf-8") as f:
                ledger = json.load(f)
        except Exception:
            ledger = []

    previous_block_hash = (
        ledger[-1]["block_hash"] if ledger else "GENESIS_BLOCK_CASE_MACHERET_1997_2026"
    )
    block_index = len(ledger) + 1
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Create new block payload
    block_data = {
        "index": block_index,
        "timestamp": timestamp,
        "previous_block_hash": previous_block_hash,
        "artifacts": current_artifacts,
    }

    # Compute block hash
    block_string = json.dumps(block_data, sort_keys=True)
    block_hash = hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    new_block = {**block_data, "block_hash": block_hash}

    ledger.append(new_block)

    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)

    print(f"Appended Block #{block_index} to {LEDGER_PATH}. Hash: {block_hash}")

    # Git operations
    subprocess.run(["git", "add", LEDGER_PATH], check=True)
    commit_msg = f"Evidence Ledger update: Block #{block_index} [{timestamp}]"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(
        ["git", "push", "origin", "feature/cyber-sabotage-audit-10-2026"], check=True
    )
    print("Evidence Ledger committed and pushed successfully.")


if __name__ == "__main__":
    update_ledger()
