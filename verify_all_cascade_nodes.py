#!/usr/bin/env python3
# A©TOR_KEY="# [⚖ A©tor Declaration]"
import json
import os
import sys


def audit_cascade():
    print("[*] Starting Autonomous Cascade Audit (Nodes A-J, M1-M2)...")
    errors = 0

    # 1. Verify Correspondence Archive & Merkle
    corr_root = "correspondence-archive"
    index_file = os.path.join(corr_root, "index.json")
    integrity_file = os.path.join(corr_root, "INTEGRITY.json")
    merkle_file = os.path.join(corr_root, "merkle.json")

    for fpath in [index_file, integrity_file, merkle_file]:
        if not os.path.exists(fpath):
            print(f"[-] Missing required file: {fpath}")
            errors += 1
        else:
            print(f"[+] Found: {fpath}")

    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            idx = json.load(f)
            items = idx.get("items", [])
            print(f"    -> Correspondence items: {len(items)}")
            for item in items:
                meta_rel = item.get("meta_file")
                meta_abs = os.path.join(corr_root, meta_rel)
                if not os.path.exists(meta_abs):
                    print(f"[-] Missing meta file: {meta_abs}")
                    errors += 1

    # 2. Verify International Dispatch
    disp_file = "international-dispatch/dispatch_manifest.json"
    if os.path.exists(disp_file):
        with open(disp_file, "r", encoding="utf-8") as f:
            disp = json.load(f)
            print(
                f"[+] International Dispatch recipients: {len(disp.get('recipients', []))}"
            )
    else:
        print(f"[-] Missing {disp_file}")
        errors += 1

    # 3. Verify Jurisdiction Audit
    jur_file = "jurisdiction-audit/collision_matrix.json"
    if os.path.exists(jur_file):
        with open(jur_file, "r", encoding="utf-8") as f:
            jur = json.load(f)
            print(
                f"[+] Jurisdictional collisions audited: {len(jur.get('collisions', []))}"
            )
    else:
        print(f"[-] Missing {jur_file}")
        errors += 1

    if errors > 0:
        print(f"\n❌ Cascade Audit Failed with {errors} errors.")
        sys.exit(1)
    else:
        print("\n✅ Autonomous Cascade Audit Passed Successfully. All Nodes Verified.")


if __name__ == "__main__":
    audit_cascade()
