#!/usr/bin/env python3
"""
Universal JSON and NDJSON / JSON Stream Validator.
Validates standard JSON files via json.loads and stream/NDJSON logs via JSONDecoder.raw_decode.
"""

import sys
import json
from pathlib import Path


def validate_file(file_path: Path) -> bool:
    print(f"[*] Validating: {file_path}")
    if not file_path.exists():
        print(f"[-] Error: File not found: {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")
    if not content.strip():
        print("[*] File is empty (skipped).")
        return True

    # First try standard JSON loading
    try:
        json.loads(content)
        print(f"[+] Valid standard JSON: {file_path}")
        return True
    except json.JSONDecodeError:
        # Fall back to stream / NDJSON / multi-object validation
        pass

    decoder = json.JSONDecoder()
    pos = 0
    count = 0
    errors = 0

    while pos < len(content):
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break
        try:
            _, idx = decoder.raw_decode(content, pos)
            pos = idx
            count += 1
        except json.JSONDecodeError as e:
            print(f"[-] JSONDecodeError in {file_path} at char {pos}: {e}")
            errors += 1
            break

    print(f"[*] Stream validated {count} objects with {errors} errors.")
    return errors == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [Path(p) for p in sys.argv[1:]]
    else:
        targets = [Path("audit_log.json")]

    all_passed = True
    for target in targets:
        if target.is_dir():
            files = list(target.glob("**/*.json")) + list(target.glob("**/*.ndjson"))
        else:
            files = [target]

        for f in files:
            if not validate_file(f):
                all_passed = False

    sys.exit(0 if all_passed else 1)
