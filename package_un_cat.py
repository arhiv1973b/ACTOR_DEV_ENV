import os
import json
import hashlib
from datetime import datetime

UN_CAT_FILES = [
    "UN_CAT_COVER_LETTER_2026.md",
    "UN_CAT_QUESTIONNAIRE_MAPPING.yaml",
    "CASE_MACHERET_1997_2026_DOSSIER.pdf",
    "CASE_MACHERET_1997_2026_DOSSIER.md",
    "INTEGRITY_WITNESS.json",
    "TI_ULA_Master.dot",
]


def main():
    package_records = []
    missing_files = []

    for fname in UN_CAT_FILES:
        if os.path.exists(fname):
            size = os.path.getsize(fname)
            sha = hashlib.sha256()
            with open(fname, "rb") as bf:
                while chunk := bf.read(65536):
                    sha.update(chunk)
            package_records.append(
                {
                    "filename": fname,
                    "size_bytes": size,
                    "sha256": sha.hexdigest(),
                    "status": "verified_present",
                }
            )
        else:
            missing_files.append(fname)

    manifest = {
        "package_id": "UN_CAT_SUBMISSION_VECTOR_2_2026",
        "protocol": "TI-ULA Cryptographic Evidence Vault",
        "recipient": "United Nations Committee Against Torture (UN CAT) - Article 22 Procedure",
        "author": "Alexei Macheret (A©tor)",
        "state_party": "Republic of Moldova",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_files": len(package_records),
        "missing_files": missing_files,
        "files": package_records,
        "submission_status": "ready_for_ohchr_upload",
    }

    out_manifest = "UN_CAT_SUBMISSION_MANIFEST_2026.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(
        f"Success: UN CAT submission package assembled. Manifest written to {out_manifest}."
    )
    print(
        f"Total verified files: {len(package_records)}, Missing: {len(missing_files)}"
    )


if __name__ == "__main__":
    main()
