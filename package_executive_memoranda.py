import os
import json
import hashlib
from datetime import datetime

MEMORANDA_FILES = [
    "MEMORANDUM_IMPUTED_LIABILITY_RM_2026.md",
    "UN_SPECIAL_RAPPORTEURS_SUBMISSIONS_2026.md",
    "CASE_MACHERET_1997_2026_DOSSIER.pdf",
    "INTEGRITY_WITNESS.json",
    "UN_CAT_SUBMISSION_MANIFEST_2026.json",
]


def main():
    records = []
    missing = []

    for fname in MEMORANDA_FILES:
        if os.path.exists(fname):
            size = os.path.getsize(fname)
            sha = hashlib.sha256()
            with open(fname, "rb") as bf:
                while chunk := bf.read(65536):
                    sha.update(chunk)
            records.append(
                {
                    "filename": fname,
                    "size_bytes": size,
                    "sha256": sha.hexdigest(),
                    "status": "verified_present",
                }
            )
        else:
            missing.append(fname)

    manifest = {
        "manifest_id": "EXECUTIVE_MEMORANDUM_PACKAGE_VECTOR_3_2026",
        "protocol": "TI-ULA Cryptographic Evidence Vault",
        "scope": "CASE-MACHERET-1997-2026",
        "targets": [
            "National Prosecutor General's Office & Ministry of Justice (RM)",
            "UN Special Rapporteurs (Torture & Independence of Judges)",
        ],
        "author": "Alexei Macheret (A©tor)",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_documents": len(records),
        "missing_documents": missing,
        "documents": records,
        "deployment_status": "ready_for_dispatch",
    }

    out_manifest = "EXECUTIVE_MEMORANDUM_MANIFEST_2026.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(
        f"Success: Executive Memoranda package assembled. Manifest written to {out_manifest}."
    )
    print(f"Verified documents: {len(records)}, Missing: {len(missing)}")


if __name__ == "__main__":
    main()
