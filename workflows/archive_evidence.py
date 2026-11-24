from __future__ import annotations
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fp:
        while chunk := fp.read(65536):
            digest.update(chunk)
    return digest.hexdigest()


def archive_file(pdf_path: Path):
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    page_count = len(reader.pages)
    if page_count == 0:
        raise RuntimeError(f"Empty PDF: {pdf_path}")

    original_name = pdf_path.name
    pdf_hash = sha256_file(pdf_path)

    evidence_dir = Path("artifacts") / "evidence" / "sha256"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    target_pdf = evidence_dir / f"{pdf_hash}.pdf"
    target_manifest = evidence_dir / f"{pdf_hash}.json"

    if target_pdf.exists():
        pdf_path.unlink()
    else:
        shutil.move(str(pdf_path), str(target_pdf))

    if sha256_file(target_pdf) != pdf_hash:
        raise RuntimeError("CAS integrity failure")

    manifest = {
        "sha256": pdf_hash,
        "algorithm": "sha256",
        "media_type": "application/pdf",
        "original_name": original_name,
        "cas_object": target_pdf.name,
        "cas_path": str(target_pdf),
        "size_bytes": target_pdf.stat().st_size,
        "page_count": page_count,
        "archived_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(target_manifest, "w", encoding="utf-8") as fp:
        json.dump(manifest, fp, indent=2, ensure_ascii=False)

    return manifest


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "registry/sample_apostille.pdf"
    try:
        manifest = archive_file(Path(target))
        print(json.dumps(manifest, indent=2))
    except Exception as exc:
        print(f"Critical Error: {exc}")
        sys.exit(1)
