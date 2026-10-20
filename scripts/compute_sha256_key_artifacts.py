#!/usr/bin/env python3
"""
Compute SHA-256 digests for key artifacts related to
FINCOMBANK_GITHUB_BILLING_ANCHOR and PR #2 evidence set.

Usage (from repository root):
    python scripts/compute_sha256_key_artifacts.py
"""

import hashlib
from pathlib import Path
from datetime import datetime, timezone

FILES_TO_HASH = [
    "evidence/financial_sabotage/FINCOMBANK_GITHUB_BILLING_ANCHOR.md",
    "transaction_c99741_master_record.json",
    "evidence_dag.json",
    "pdf_manifest.json",
    # Add more paths as needed after primary evidence intake
]

def compute_sha256(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        return "FILE_NOT_FOUND"
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

if __name__ == "__main__":
    print(f"# SHA-256 Manifest — generated {datetime.now(timezone.utc).isoformat()}")
    print(f"# Case: CASE-MACHERET-1997-2026")
    print(f"# Related: FT-SUMMARY-20261020-L0 / PR #2")
    print()
    for file_path in FILES_TO_HASH:
        digest = compute_sha256(file_path)
        print(f"{digest}  {file_path}")
