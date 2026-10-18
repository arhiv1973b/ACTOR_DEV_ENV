#!/usr/bin/env python3
"""
TI-ULA Missing Evidence Audit Report Generator
Generates JSON and CSV audit reports listing any missing physical binary files and their SHA-256 hashes.
"""

import os
import json
import csv
import yaml

MANIFEST_PATH = (
    r"H:\ACTOR_DEV_ENV\artifacts\reabilitare\TI_ULA_MASTER_DAG_REGISTRY_2026.yaml"
)
REPORT_JSON = r"H:\ACTOR_DEV_ENV\missing_evidence_audit_report.json"
REPORT_CSV = r"H:\ACTOR_DEV_ENV\missing_evidence_audit_report.csv"


def generate_report():
    print("Generating missing evidence audit report...")
    if not os.path.exists(MANIFEST_PATH):
        print(f"Manifest not found: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    hash_registry = data.get("hash_registry", {})
    missing_items = []

    for sha256, info in hash_registry.items():
        master = info.get("master_file")
        if master and not os.path.exists(master):
            missing_items.append(
                {
                    "sha256": sha256,
                    "role": "master_file",
                    "path": master,
                    "size_bytes": info.get("size_bytes", 0),
                }
            )

        for dup in info.get("duplicates", []):
            if not os.path.exists(dup):
                missing_items.append(
                    {
                        "sha256": sha256,
                        "role": "duplicate",
                        "path": dup,
                        "size_bytes": info.get("size_bytes", 0),
                    }
                )

    report_data = {
        "audit_timestamp": data.get("timestamp"),
        "total_missing": len(missing_items),
        "missing_evidence": missing_items,
    }

    # Save JSON report
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    # Save CSV report
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sha256", "role", "path", "size_bytes"])
        writer.writeheader()
        for item in missing_items:
            writer.writerow(item)

    print(f"Audit reports generated successfully:\n- {REPORT_JSON}\n- {REPORT_CSV}")


if __name__ == "__main__":
    generate_report()
