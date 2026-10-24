#!/usr/bin/env python3
"""
anchor_ipfs_zenodo.py
Decentralized Anchoring & Zenodo DOI / IPFS Metadata Generator
Subject: Macheret (IDNP: 2000001159655)
"""

import hashlib
import json
import os

BASE_DIR = r"H:\ACTOR_DEV_ENV"
REPORT_PATH = os.path.join(BASE_DIR, "ERGA_OMNES_AUDIT_REPORT_2026.txt")
MANIFEST_PATH = os.path.join(
    BASE_DIR, "05_CRYPTO_MANIFESTS", "ACTOR_MANIFEST_SIGNATURE.json"
)
OUTPUT_ZENODO = os.path.join(BASE_DIR, "zenodo_deposit_metadata.json")
OUTPUT_IPFS = os.path.join(BASE_DIR, "ipfs_decentralized_anchor.json")


def compute_sha256(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    report_sha = compute_sha256(REPORT_PATH)
    manifest_sha = compute_sha256(MANIFEST_PATH)

    # 1. Zenodo DOI Metadata payload
    zenodo_payload = {
        "metadata": {
            "title": (
                "Global Cryptographic Audit Report & Erga Omnes Anchor (Case Macheret)"
            ),
            "upload_type": "publication",
            "publication_type": "report",
            "description": (
                "Mathematical Zero-Collision audit report and Jus Cogens"
                " compliance proof for Subject Macheret (IDNP: 2000001159655)."
                " Anchored via SHA-256 ledger and Erga Omnes standards."
            ),
            "creators": [
                {
                    "name": "Macheret, Alexei",
                    "affiliation": "Independent Human Rights Claimant",
                }
            ],
            "access_right": "open",
            "license": "cc-by-4.0",
            "keywords": [
                "Jus Cogens",
                "Erga Omnes",
                "Human Rights",
                "Cryptographic Ledger",
                "SHA-256",
                "UDHR 1948",
            ],
        }
    }

    with open(OUTPUT_ZENODO, "w", encoding="utf-8") as f:
        json.dump(zenodo_payload, f, indent=4, ensure_ascii=False)
    print(f"[+] Zenodo DOI metadata generated: {OUTPUT_ZENODO}")

    # 2. IPFS Decentralized Anchor Manifest
    ipfs_payload = {
        "protocol": "IPFS/ErgaOmnes-ZeroCollision",
        "subject": "Macheret",
        "idnp": "2000001159655",
        "artifacts": {
            "ERGA_OMNES_AUDIT_REPORT_2026.txt": {
                "sha256": report_sha,
                "simulated_cid": (
                    f"Qm" + (report_sha[:42] if report_sha else "0" * 42)
                ),
            },
            "ACTOR_MANIFEST_SIGNATURE.json": {
                "sha256": manifest_sha,
                "simulated_cid": (
                    f"Qm" + (manifest_sha[:42] if manifest_sha else "0" * 42)
                ),
            },
        },
    }

    with open(OUTPUT_IPFS, "w", encoding="utf-8") as f:
        json.dump(ipfs_payload, f, indent=4, ensure_ascii=False)
    print(f"[+] IPFS Decentralized Anchor Manifest generated: {OUTPUT_IPFS}")


if __name__ == "__main__":
    main()
