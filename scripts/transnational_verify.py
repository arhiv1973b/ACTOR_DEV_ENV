#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [⚖ A©tor Declaration]
Transnational Verification & Certificate Differential Engine
Author: Alexei Macheret (A©tor)
IDNP: 2000001159655
Scope: Jus Cogens, Erga Omnes, UDHR 1948, Hague Convention 1961
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timezone
import requests

try:
    from pyhanko.pdf_utils.reader import PdfFileReader

    PYHANKO_AVAILABLE = True
except Exception:
    PYHANKO_AVAILABLE = False

DOWNLOADS = Path("downloads")
REPORTS = Path("reports")
MANIFESTS = Path("05_CRYPTO_MANIFESTS")

for folder in (DOWNLOADS, REPORTS, MANIFESTS):
    folder.mkdir(parents=True, exist_ok=True)


def build_apostille_url(apostille_code, security_code):
    """Constructs a clean, valid URL for the official Apostille download endpoint without HTML artifacts."""
    return (
        "https://apostila.gov.md/apostila/site/"
        f"downloadApostila/apostileCode/{apostille_code}"
        f"/securityCode/{security_code}"
    )


def quick_signature_check(pdf_path):
    result = {"signed": False, "signature_count": 0}
    if not PYHANKO_AVAILABLE:
        return result
    try:
        with open(pdf_path, "rb") as f:
            reader = PdfFileReader(f)
            signatures = list(reader.embedded_signatures)
            result["signature_count"] = len(signatures)
            result["signed"] = len(signatures) > 0
    except Exception as ex:
        result["error"] = str(ex)
    return result


def process_transnational_record(apostille_code, security_code, proxy_url=None):
    url = build_apostille_url(apostille_code, security_code)

    headers = {
        "User-Agent": "Mozilla/5.0 International-Apostille-Verifier/4.0",
        "Accept": "application/pdf,application/xhtml+xml,*/*",
    }

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    response = None
    success = False

    for attempt in range(5):
        try:
            response = requests.get(
                url, headers=headers, timeout=45, allow_redirects=True, proxies=proxies
            )
            if response.status_code != 200:
                time.sleep(2**attempt)
                continue

            content_type = response.headers.get("Content-Type", "").lower()
            if "pdf" not in content_type:
                raise ValueError(f"Unexpected content type: {content_type}")

            success = True
            break
        except Exception as ex:
            print(f"[!] Attempt {attempt + 1}: {ex}")
            time.sleep(2**attempt)

    if not success or not response:
        return {
            "apostille_code": apostille_code,
            "security_code": security_code,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_state": "download_failed",
        }

    content = response.content
    if not content.startswith(b"%PDF"):
        raise ValueError("Downloaded object is not a PDF.")

    final_url = response.url
    redirected = final_url != url
    sha256_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)

    pdf_path = DOWNLOADS / f"{apostille_code}.pdf"
    pdf_path.write_bytes(content)

    signature_info = quick_signature_check(pdf_path)

    manifest = {
        "apostille_code": apostille_code,
        "security_code": security_code,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "http_status": response.status_code,
        "redirected": redirected,
        "redirect_chain": [h.url for h in response.history],
        "final_url": final_url,
        "sha256": sha256_hash,
        "file_size": file_size,
        "pdf_signature": signature_info,
        "local_file": str(pdf_path),
        "network_mode": "direct_https_request",
        "verification_state": "download_success",
    }

    manifest_path = MANIFESTS / f"{apostille_code}_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"[+] SUCCESS {apostille_code}")
    print(f"[+] SHA256 {sha256_hash}")
    return manifest


def main():
    sample_apostille = "IMWM44AZGX6N6"
    sample_security = "2013073817848"
    result = process_transnational_record(sample_apostille, sample_security)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    main()
