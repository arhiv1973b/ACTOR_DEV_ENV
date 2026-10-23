import os
import json
import hashlib
from datetime import datetime, timezone

# TI-ULA CONVERGENCE CYCLE III: CADASTRAL & MUNICIPAL ARCHIVE ANCHORING
# Case: CASE-MACHERET-1997-2026 | Location Node: Chișinău
# Protocol: UDHR-Override (Article 8 - Effective Remedy)

TARGET_VAULTS = [
    "CADASTRAL_RECORDS",
    "MUNICIPAL_ARCHIVE_DUPLICATES",
    "PROPERTY_ALLOCATIONS",
]
MANIFEST_PATH = "ti_ula_convergence_cycle_iii.json"


def anchor_municipal_evidence():
    print("=== TI-ULA CYCLE III: INITIATING CADASTRAL & ARCHIVE ANCHORING ===")
    anchors = []

    for vault in TARGET_VAULTS:
        if not os.path.exists(vault):
            os.makedirs(vault, exist_ok=True)
            print(f"[+] Initialized missing vault directory: {vault}")

        for root, _, files in os.walk(vault):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()

                    sha256_hash = hashlib.sha256(data).hexdigest()
                    anchors.append(
                        {
                            "node_type": "physical_document_scan",
                            "path": filepath,
                            "sha256": sha256_hash,
                            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                            "udhr_binding": "Article 8",
                        }
                    )
                except Exception as e:
                    print(f"[ERROR] Failed to read {filepath}: {e}")

    cycle_iii_manifest = {
        "cycle": "III_MUNICIPAL_CADASTRAL_SEAL",
        "case_id": "CASE-MACHERET-1997-2026",
        "total_anchored": len(anchors),
        "cryptographic_locks": anchors,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(cycle_iii_manifest, f, indent=4, ensure_ascii=False)

    print(
        f"[✓] Cycle III Manifest secured: {MANIFEST_PATH} ({len(anchors)} municipal records locked)."
    )


if __name__ == "__main__":
    anchor_municipal_evidence()
