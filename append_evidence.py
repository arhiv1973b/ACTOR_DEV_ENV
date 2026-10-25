import json
import hashlib
import datetime
from pathlib import Path

LEDGER_NDJSON = "audit_log.ndjson"


def append_evidence(file_path, description, author="Macheret Alexei (A©tor)"):
    p = Path(file_path)
    if not p.exists():
        print(f"❌ Error: Evidence file {file_path} not found.")
        return

    file_bytes = p.read_bytes()
    file_sha256 = hashlib.sha256(file_bytes).hexdigest()

    # Читаем последний хэш блока для соблюдения цепочки
    prev_hash = "GENESIS_BLOCK_CASE_MACHERET_1997_2026"
    index = 1
    ledger_path = Path(LEDGER_NDJSON)
    if ledger_path.exists():
        lines = [
            l.strip()
            for l in ledger_path.read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        if lines:
            try:
                last_record = json.loads(lines[-1])
                prev_hash = last_record.get("block_hash", prev_hash)
                index = last_record.get("index", 0) + 1
            except Exception:
                pass

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    record = {
        "index": index,
        "previous_block_hash": prev_hash,
        "timestamp": timestamp,
        "author": author,
        "email": "alexeimaceret7@gmail.com",
        "subject": f"Evidence Ingestion: {p.name}",
        "evidence_file": str(p),
        "evidence_sha256": file_sha256,
        "description": description,
        "protocol": "A©tor Jus Cogens Ledger",
        "signature_key": 'A©TOR_KEY="# [⚖ A©tor Declaration]"',
    }

    record_str = json.dumps(record, sort_keys=True)
    block_hash = hashlib.sha256(record_str.encode("utf-8")).hexdigest()
    record["block_hash"] = block_hash

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

    print(
        f"✅ Evidence successfully integrated into block #{index} (Hash: {block_hash[:12]}...)"
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        append_evidence(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python append_evidence.py <file_path> <description>")
