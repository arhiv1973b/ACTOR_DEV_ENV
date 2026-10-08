import json
import os
import hashlib

ARTIFACTS = [
    "macheret_identity_mapping_forensic.json",
    "macheret_identity_mapping_forensic.yaml",
    "artifacts/reabilitare/macheret_identity_mapping_forensic.json",
    "artifacts/reabilitare/macheret_identity_mapping_forensic.yaml",
    "artifacts/reabilitare/FINANCIAL_TRANSACTION_UN_SUPPORT_02MAY2025.yaml",
    "artifacts/reabilitare/EVIDENCE_POINTER_UN_SUPPORT_02MAY2025.json",
]


def verify_artifacts():
    print("[*] Starting local forensic capture and artifact verification...")
    ledger = {}
    for path in ARTIFACTS:
        if os.path.exists(path):
            with open(path, "rb") as f:
                content = f.read()
                file_hash = hashlib.sha256(content).hexdigest()
            ledger[path] = {
                "status": "VERIFIED",
                "sha256": file_hash,
                "size_bytes": len(content),
            }
            print(f"[OK] {path} -> SHA256: {file_hash[:16]}...")
        else:
            ledger[path] = {"status": "MISSING"}
            print(f"[ERROR] Missing: {path}")

    with open(
        "artifacts/reabilitare/forensic_capture_ledger.json", "w", encoding="utf-8"
    ) as out:
        json.dump(ledger, out, indent=4)
    print("[*] Forensic ledger captured successfully.")


if __name__ == "__main__":
    verify_artifacts()
