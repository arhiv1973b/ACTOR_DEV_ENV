#!/usr/bin/env python3
"""
TI-ULA Binary Existence & Chain of Custody Verifier
Checks whether physical files corresponding to FilePath / MasterFile nodes actually exist on disk.
Updates status flags (binaryExists: true/false).
"""

import os
import json
import yaml

MANIFEST_PATH = r"H:\ACTOR_DEV_ENV\ti_ula_manual_binder_manifest.yaml"


def verify_binaries():
    print("Verifying physical binary existence across workspace...")
    if not os.path.exists(MANIFEST_PATH):
        print(f"Manifest not found: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    hash_registry = data.get("hash_registry", {})
    total_files = 0
    missing_files = 0

    for sha256, info in hash_registry.items():
        master = info.get("master_file")
        if master:
            total_files += 1
            exists = os.path.exists(master)
            info["binary_exists"] = exists
            if not exists:
                missing_files += 1
                print(f"MISSING BINARY: {master}")

        for dup in info.get("duplicates", []):
            total_files += 1
            exists = os.path.exists(dup)
            if not exists:
                missing_files += 1
                print(f"MISSING DUPLICATE: {dup}")

    data["verification_summary"] = {
        "total_checked": total_files,
        "missing_binaries": missing_files,
        "integrity_status": "VERIFIED_ALL_PRESENT"
        if missing_files == 0
        else "WARNING_MISSING_FILES",
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print(
        f"Verification complete. Total checked: {total_files}, Missing: {missing_files}"
    )


if __name__ == "__main__":
    verify_binaries()
