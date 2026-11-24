import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        while chunk := fp.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_all():
    evidence_dir = Path("artifacts") / "evidence" / "sha256"
    manifests = list(evidence_dir.glob("*.json"))

    if not manifests:
        raise RuntimeError("No manifests found")

    for manifest_file in manifests:
        with open(manifest_file, encoding="utf-8") as fp:
            manifest = json.load(fp)

        pdf_path = evidence_dir / manifest["cas_object"]

        if not pdf_path.exists():
            raise RuntimeError(f"Missing object: {pdf_path}")

        digest = sha256_file(pdf_path)
        if digest != manifest["sha256"]:
            raise RuntimeError(f"Hash mismatch: {pdf_path}")

        print(f"Verified {manifest['sha256']}")


if __name__ == "__main__":
    try:
        verify_all()
    except Exception as exc:
        print(exc)
        sys.exit(1)
