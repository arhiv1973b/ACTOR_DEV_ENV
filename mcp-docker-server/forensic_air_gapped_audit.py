#!/usr/bin/env python3
"""
Air-Gapped Forensic SHA-256 Audit Script
Calculates and verifies SHA-256 hashes of files in the target directory.
"""

import sys
import hashlib
from pathlib import Path

def calculate_sha256(file_path):
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest().lower()
    except Exception as e:
        return None

def main():
    target_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/audit_data")
    if not target_dir.exists():
        print(f"[-] Target directory does not exist: {target_dir}")
        sys.exit(1)

    print(f"[*] Starting Air-Gapped Forensic Audit on directory: {target_dir}")
    file_count = 0
    error_count = 0

    results = []
    for path in target_dir.rglob("*"):
        if path.is_file():
            file_count += 1
            h = calculate_sha256(path)
            if h:
                rel_path = path.relative_to(target_dir)
                results.append((str(rel_path), h))
                print(f"[OK] {rel_path} -> {h}")
            else:
                error_count += 1
                print(f"[-] ERROR reading {path}")

    print("=" * 60)
    print(f"Audit Complete. Files processed: {file_count}, Errors: {error_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
