#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [⚖ A©tor Declaration]
Transnational Verification & Certificate Differential Engine (Corrected)
Author: Alexei Macheret (A©tor) | IDNP: 2000001159655
Scope: Jus Cogens, Erga Omnes, UDHR 1948, Hague Convention 1961
"""

import os
import json
import hashlib
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

try:
    from pyhanko.pdf_utils.reader import PdfFileReader

    PYHANKO_AVAILABLE = True
except ImportError:
    PdfFileReader = None
    PYHANKO_AVAILABLE = False

# Paths configuration
DOWNLOADS = Path("downloads")
MANIFESTS = Path("05_CRYPTO_MANIFESTS")

for folder in (DOWNLOADS, MANIFESTS):
    folder.mkdir(parents=True, exist_ok=True)


def build_apostille_url(apostille_code, security_code):
    """Constructs a clean, valid URL for the official Apostille download endpoint."""
    return (
        "https://apostila.gov.md/apostila/site/"
        f"downloadApostila/apostileCode/{apostille_code}"
        f"/securityCode/{security_code}"
    )


def quick_signature_check(pdf_path):
    """Inspects PDF for embedded digital signatures using pyhanko."""
    result = {"signed": False, "signature_count": 0}
    if not PYHANKO_AVAILABLE or PdfFileReader is None:
        result["error"] = "pyhanko not available"
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
    """
    Downloads, validates MIME and PDF magic bytes, computes SHA-256 hash,
    inspects digital signatures, tracks redirects and TLS, and generates manifest.
    """
    url = build_apostille_url(apostille_code, security_code)

    headers = {
        "User-Agent": "Mozilla/5.0 International-Apostille-Verifier/4.0",
        "Accept": "application/pdf,application/xhtml+xml,*/*",
    }

    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

    response = None
    success = False

    # Exponential backoff retries
    for attempt in range(5):
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, timeout=45, allow_redirects=True
            )
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "").lower()
                if "pdf" in content_type:
                    success = True
                    break
                else:
                    # Non-PDF response is likely a permanent error page, stop retrying
                    return {
                        "apostille_code": apostille_code,
                        "security_code": security_code,
                        "download_timestamp": datetime.now(timezone.utc).isoformat(),
                        "verification_state": "download_failed",
                        "error": f"Unexpected content type: {content_type}",
                    }
            time.sleep(2**attempt)
        except requests.RequestException as e:
            print(f"[!] Request exception on attempt {attempt + 1}: {e}")
            time.sleep(2**attempt)

    if not success or not response or response.status_code != 200:
        return {
            "apostille_code": apostille_code,
            "security_code": security_code,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "http_status": response.status_code if response else 0,
            "verification_state": "download_failed",
        }

    content = response.content

    if not content.startswith(b"%PDF"):
        return {
            "apostille_code": apostille_code,
            "security_code": security_code,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_state": "download_failed",
            "error": "Not a valid PDF binary stream",
        }

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

    print(
        f"[+] Success. Apostille: {apostille_code} | SHA-256: {sha256_hash} | Signed: {signature_info.get('signed')}"
    )
    return manifest


if __name__ == "__main__":
    sample_apostille = "IMWM44AZGX6N6"
    sample_sec_code = "2013073817848"

    result = process_transnational_record(sample_apostille, sample_sec_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
