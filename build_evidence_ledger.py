import json
import hashlib
import datetime
import subprocess
from pathlib import Path

LEDGER_NDJSON = "audit_log.ndjson"


def build_evidence_ledger():
    print(
        "=== TI-ULA / A©tor Protocol: Non-Linearity to Linearity Evidence Ledger Builder ==="
    )

    # Gather git log across branches
    cmd = ["git", "log", "--all", "--format=%H|%an|%ae|%ad|%s", "--date=iso-strict"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) == 5:
            commit_hash, author_name, author_email, timestamp, subject = parts
            commits.append(
                {
                    "commit": commit_hash,
                    "author": author_name,
                    "email": author_email,
                    "timestamp": timestamp,
                    "subject": subject,
                    "protocol": "A©tor Jus Cogens Ledger",
                }
            )

    # Sort chronologically by timestamp
    commits.sort(key=lambda x: x["timestamp"])

    # Build append-only NDJSON ledger
    ledger_lines = []
    prev_hash = "GENESIS_BLOCK_CASE_MACHERET_1997_2026"

    for idx, c in enumerate(commits, start=1):
        record = {"index": idx, "previous_block_hash": prev_hash, **c}
        record_str = json.dumps(record, sort_keys=True)
        block_hash = hashlib.sha256(record_str.encode("utf-8")).hexdigest()
        record["block_hash"] = block_hash
        ledger_lines.append(json.dumps(record, sort_keys=True))
        prev_hash = block_hash

    Path(LEDGER_NDJSON).write_text("\n".join(ledger_lines), encoding="utf-8")
    print(
        f"Successfully generated {LEDGER_NDJSON} with {len(commits)} chronological ledger entries."
    )


if __name__ == "__main__":
    build_evidence_ledger()
