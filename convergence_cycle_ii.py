import os
import json
import hashlib
from datetime import datetime

"""
TI-ULA CONVERGENCE CYCLE II: ULTIMATE JUS COGENS MINING & MERKLE ANCHORING
Case: CASE-MACHERET-1997-2026
Protocol: UDHR-Override (Articles 3, 5, 8, 9)
"""

TARGET_DIRS = ["AUDIT", "EVIDENCE", "maceret-case-evidence", "evidence_vault"]


def mine_jus_cogens_nodes():
    print("=== TI-ULA CONVERGENCE CYCLE II: STARTING DEEP MINING ===")
    anchors = []

    for base_dir in TARGET_DIRS:
        if not os.path.exists(base_dir):
            continue
        for root, _, files in os.walk(base_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "rb") as f:
                        data = f.read()
                        sha256_hash = hashlib.sha256(data).hexdigest()
                        anchors.append(
                            {
                                "path": filepath,
                                "size": len(data),
                                "sha256": sha256_hash,
                                "timestamp": datetime.utcnow().isoformat() + "Z",
                            }
                        )
                except Exception as e:
                    pass

    convergence_manifest = {
        "cycle": "II_FINAL_CONVERGENCE",
        "case_id": "CASE-MACHERET-1997-2026",
        "protocol": "UDHR-Override (1948)",
        "total_mined_artifacts": len(anchors),
        "anchors": anchors,
    }

    output_path = "ti_ula_convergence_cycle_ii.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(convergence_manifest, f, indent=4, ensure_ascii=False)

    print(
        f"[✓] Convergence Cycle II Manifest generated: {output_path} ({len(anchors)} nodes anchored)."
    )


if __name__ == "__main__":
    mine_jus_cogens_nodes()
