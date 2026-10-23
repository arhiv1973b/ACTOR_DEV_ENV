#!/usr/bin/env python3
"""
A©tor UN Evidence Packet Exporter
CASE-MACHERET-1997-2026 | TI-ULA

Reads proofs/manifest.json and produces a machine-readable
proofs/un_evidence_bundle.json suitable for transmission to
UN Special Procedures monitoring structures.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "proofs" / "manifest.json"
OUTPUT_PATH = REPO_ROOT / "proofs" / "un_evidence_bundle.json"


def main() -> int:
    if not MANIFEST_PATH.exists():
        print(f"[FAIL] Manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        return 1

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    bundle = {
        "bundle_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": manifest.get("case_id"),
        "actor_key": manifest.get("actor_key"),
        "subject": manifest.get("subject"),
        "un_reference": "tw57lryb",
        "legal_framework": manifest.get("legal_framework", {}),
        "repository": manifest.get("repository"),
        "files": [],
        "udhr_summary": {"5": [], "6": [], "7": [], "8": [], "17": []},
    }

    for entry in manifest.get("files", []):
        file_rec = {
            "id": entry.get("id"),
            "path": entry.get("path"),
            "description": entry.get("description"),
            "sha256": entry.get("sha256"),
            "size_bytes": entry.get("size_bytes"),
            "mime_type": entry.get("mime_type"),
            "date": entry.get("date"),
            "udhr_articles": entry.get("udhr_articles", []),
            "tags": entry.get("tags", []),
            "google_drive_view_link": entry.get("google_drive_view_link"),
            "google_drive_file_id": entry.get("google_drive_file_id"),
        }
        bundle["files"].append(file_rec)

        for art in entry.get("udhr_articles", []):
            key = str(art)
            if key in bundle["udhr_summary"]:
                bundle["udhr_summary"][key].append(entry.get("id"))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)

    print(f"[OK] Bundle written: {OUTPUT_PATH}")
    print(f"     Files included: {len(bundle['files'])}")
    for art, ids in bundle["udhr_summary"].items():
        print(f"     UDHR Art. {art}: {len(ids)} artifact(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
