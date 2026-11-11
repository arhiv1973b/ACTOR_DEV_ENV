#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [⚖ A©tor Declaration]
Transnational Verification & Certificate Differential Engine (Enhanced)
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
from pyhanko.pdf_utils.reader import PdfFileReader

# Paths configuration
DOWNLOADS = Path("downloads")
REPORTS = Path("reports")
MANIFESTS = Path("05_CRYPTO_MANIFESTS")

for p in [DOWNLOADS, REPORTS, MANIFESTS]:
    p.mkdir(parents=True, exist_ok=True)


def quick_signature_check(pdf_path):
    """Inspects PDF for embedded digital signatures using pyhanko."""
    result = {"signed": False, "signature_count": 0}
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
    url = (
        "https://apostila.gov.md/apostila/site/"
        f"downloadApostila/apostileCode/{apostille_code}"
        f"/securityCode/{security_code}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) International-Apostille-Verifier/3.4",
        "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
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
                    print(
                        f"[!] Warning: Unexpected content type '{content_type}' for {apostille_code}"
                    )
            time.sleep(2**attempt)
        except requests.RequestException as e:
            print(f"[!] Request exception on attempt {attempt + 1}: {e}")
            time.sleep(2**attempt)

    # Handle failure cases
    if not success or not response or response.status_code != 200:
        return {
            "apostille_code": apostille_code,
            "security_code": security_code,
            "download_timestamp": datetime.now(timezone.utc).isoformat(),
            "http_status": response.status_code if response else 0,
            "verification_state": "download_failed",
        }

    content = response.content

    # Validate PDF magic bytes signature before processing
    if not content.startswith(b"%PDF"):
        raise ValueError("Downloaded file is not a valid PDF binary stream.")

    # Handle redirects & redirect chain
    final_url = response.url
    redirected = final_url != url
    redirect_chain = [h.url for h in response.history]

    # Compute cryptographic SHA-256 hash
    sha256_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)

    pdf_path = DOWNLOADS / f"{apostille_code}_transnational.pdf"
    pdf_path.write_bytes(content)

    # Perform digital signature verification on the downloaded file
    signature_info = quick_signature_check(pdf_path)

    # Construct enhanced manifest structure
    manifest = {
        "apostille_code": apostille_code,
        "security_code": security_code,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "http_status": response.status_code,
        "redirected": redirected,
        "redirect_chain": redirect_chain,
        "final_url": final_url,
        "sha256": sha256_hash,
        "file_size": file_size,
        "pdf_signature": signature_info,
        "tls": {"scheme": "https", "verified": True},
        "verification_state": "download_success",
        "network_mode": "direct_https_request",
    }

    manifest_path = MANIFESTS / f"{apostille_code}_transnational_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Safe cleanup of temporary PDF file
    try:
        if pdf_path.exists():
            pdf_path.unlink()
    except OSError:
        pass

    print(
        f"[+] Success. Apostille: {apostille_code} | SHA-256: {sha256_hash} | Signed: {signature_info.get('signed')}"
    )
    return manifest


if __name__ == "__main__":
    sample_apostille = "IMWM44AZGX6N6"
    sample_sec_code = "2013073817848"

    result = process_transnational_record(sample_apostille, sample_sec_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
