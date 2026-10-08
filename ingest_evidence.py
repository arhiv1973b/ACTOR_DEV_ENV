# ingest_evidence.py
import os
import shutil
import hashlib
import json

RAW_EVIDENCE_DIR = "raw_evidence"
MASTER_DOSSIER_DIR = "MASTER_DOSSIER"
TARGET_IDNP = "2000001159655"
TARGET_VARIANTS = ["MACERET", "MACHERET", "МАЧЕРЕТ"]


def ensure_dirs():
    os.makedirs(RAW_EVIDENCE_DIR, exist_ok=True)
    os.makedirs(MASTER_DOSSIER_DIR, exist_ok=True)


def ingest():
    ensure_dirs()
    files = os.listdir(RAW_EVIDENCE_DIR)
    if not files:
        print(
            f"[*] No raw evidence files found in '{RAW_EVIDENCE_DIR}/'. Please place files there."
        )
        return

    print(f"[*] Starting ingestion of {len(files)} files from {RAW_EVIDENCE_DIR}...")
    ingestion_report = []

    for filename in files:
        src_path = os.path.join(RAW_EVIDENCE_DIR, filename)
        if os.path.isdir(src_path):
            continue

        with open(src_path, "rb") as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()

        # Check text content if possible
        text_content = ""
        try:
            text_content = content.decode("utf-8", errors="ignore")
        except Exception:
            pass

        idnp_found = TARGET_IDNP in text_content or TARGET_IDNP in filename
        variants_found = [
            v
            for v in TARGET_VARIANTS
            if v.lower() in text_content.lower() or v.lower() in filename.lower()
        ]

        dest_path = os.path.join(MASTER_DOSSIER_DIR, filename)
        shutil.copy2(src_path, dest_path)

        record = {
            "filename": filename,
            "sha256": file_hash,
            "idnp_verified": idnp_found,
            "matched_variants": variants_found,
            "archived_to": dest_path,
        }
        ingestion_report.append(record)
        print(
            f"[OK] Ingested '{filename}' -> SHA256: {file_hash[:16]}... | IDNP Match: {idnp_found} | Variants: {variants_found}"
        )

    ledger_path = os.path.join(MASTER_DOSSIER_DIR, "ingestion_ledger.json")
    with open(ledger_path, "w", encoding="utf-8") as out:
        json.dump(ingestion_report, out, indent=4)
    print(f"[*] Ingestion complete. Ledger saved to {ledger_path}")


if __name__ == "__main__":
    ingest()
