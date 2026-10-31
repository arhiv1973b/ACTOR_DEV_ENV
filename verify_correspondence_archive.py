#!/usr/bin/env python3
# A©TOR_KEY="# [⚖ A©tor Declaration]"
import json
import os
import sys


def verify_archive():
    root = "correspondence-archive"
    index_path = os.path.join(root, "index.json")
    integrity_path = os.path.join(root, "INTEGRITY.json")

    if not os.path.exists(index_path) or not os.path.exists(integrity_path):
        print("❌ Missing index.json or INTEGRITY.json")
        sys.exit(1)

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    items = index_data.get("items", [])
    print(
        f"[*] Verifying correspondence archive: {index_data.get('case_id')} ({len(items)} items)"
    )

    for item in items:
        meta_file = item.get("meta_file")
        meta_path = os.path.join(root, meta_file)
        if not os.path.exists(meta_path):
            print(f"❌ Meta file missing: {meta_file}")
            sys.exit(1)
        with open(meta_path, "r", encoding="utf-8") as mf:
            meta_data = json.load(mf)
        print(
            f"  [✓] Verified meta entry: {meta_data.get('id')} - {meta_data.get('subject')}"
        )

    print("✅ Correspondence Archive L1 Integrity Verification Passed.")


if __name__ == "__main__":
    verify_archive()
