#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import crypto_utils


def validate_chain(chain: list) -> list:
    """Validate chain integrity and return a list of error strings."""
    errors = []
    previous_record_hash = None

    for index, record in enumerate(chain):
        cid = record.get("custody_id", f"index-{index}")

        # 1. Validate current record integrity
        actual_hash = record.get("record_sha256")

        if actual_hash is None:
            errors.append(f"{cid}: missing record_sha256")
            continue
        elif not crypto_utils.validate_sha256(actual_hash):
            errors.append(f"{cid}: invalid record_sha256 format")
            continue

        expected_hash = crypto_utils.canonical_record_hash(record)

        if actual_hash.lower() != expected_hash.lower():
            errors.append(f"{cid}: record_sha256 mismatch")
            continue

        validated_record_hash = actual_hash.lower()

        # 2. Validate chain links
        if index == 0:
            if record.get("previous_record_sha256") not in (None, ""):
                errors.append(f"{cid}: first record contains previous_record_sha256")
        else:
            actual_prev_hash = record.get("previous_record_sha256")
            if actual_prev_hash is None:
                errors.append(f"{cid}: missing previous_record_sha256")
            elif not crypto_utils.validate_sha256(actual_prev_hash):
                errors.append(f"{cid}: invalid previous_record_sha256 format")
            elif previous_record_hash is None:
                errors.append(
                    f"{cid}: chain broken because previous record hash is unavailable"
                )
            elif actual_prev_hash.lower() != previous_record_hash.lower():
                errors.append(f"{cid}: previous_record_sha256 mismatch")

        previous_record_hash = validated_record_hash

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_chain.py <chain_file.json/ndjson>")
        sys.exit(1)

    all_passed = True
    for path_str in sys.argv[1:]:
        chain_path = Path(path_str)
        if not chain_path.exists():
            print(f"[-] Error: Chain file not found: {chain_path}")
            all_passed = False
            continue

        with open(chain_path, "r", encoding="utf-8") as f:
            try:
                chain = json.load(f)
            except json.JSONDecodeError:
                f.seek(0)
                chain = [json.loads(line) for line in f if line.strip()]

        errors = validate_chain(chain)
        if errors:
            for err in errors:
                print(f"[-] Validation Error: {err}")
            all_passed = False
        else:
            print(f"[+] Chain {chain_path} is valid.")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
