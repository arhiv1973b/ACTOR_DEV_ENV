#!/usr/bin/env python3
"""
Minimal NDJSON (Newline-Delimited JSON) Validator Script.
Validates that every non-empty line in a file is a valid JSON object.
"""

import sys
import json
from pathlib import Path


def validate_ndjson(file_path: Path) -> bool:
    print(f"[*] Validating JSON stream/NDJSON file: {file_path}")
    if not file_path.exists():
        print(f"[-] Error: File not found: {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")
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
            print(f"[-] JSONDecodeError at char {pos}: {e}")
            errors += 1
            break

    print(f"[*] Parsed {count} valid JSON objects with {errors} errors.")
    return errors == 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("audit_log.json")
    success = validate_ndjson(target)
    sys.exit(0 if success else 1)
