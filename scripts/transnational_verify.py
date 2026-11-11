#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [⚖ A©tor Declaration]
Transnational Verification & Certificate Differential Engine
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

# Paths configuration
DOWNLOADS = Path("downloads")
REPORTS = Path("reports")
MANIFESTS = Path("05_CRYPTO_MANIFESTS")

for p in [DOWNLOADS, REPORTS, MANIFESTS]:
    p.mkdir(parents=True, exist_ok=True)


def process_transnational_record(apostille_code, security_code, proxy_url=None):
    """
    Downloads, verifies MIME-type, computes SHA-256 hash, handles redirects,
    and generates a streamlined verification manifest.
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

    # 9. Exponential backoff retries
    for attempt in range(5):
        try:
            response = requests.get(
                url, headers=headers, proxies=proxies, timeout=45, allow_redirects=True
            )
            if response.status_code == 200:
                # 3. Check MIME-type
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

    # 5. Handle redirects
    final_url = response.url
    redirected = final_url != url
    content = response.content

    # 4. Compute cryptographic SHA-256 hash before writing
    sha256_hash = hashlib.sha256(content).hexdigest()
    file_size = len(content)

    pdf_path = DOWNLOADS / f"{apostille_code}_transnational.pdf"
    pdf_path.write_bytes(content)

    # 10. Streamlined manifest structure
    manifest = {
        "apostille_code": apostille_code,
        "security_code": security_code,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "http_status": response.status_code,
        "redirected": redirected,
        "final_url": final_url,
        "sha256": sha256_hash,
        "file_size": file_size,
        "verification_state": "download_success",
        "network_mode": "direct_https_request",
    }

    manifest_path = MANIFESTS / f"{apostille_code}_transnational_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # 8. Cleanup temporary PDF file after manifest generation (aligned with FIFO carousel rules)
    if pdf_path.exists():
        pdf_path.unlink()

    print(f"[+] Success. Apostille: {apostille_code} | SHA-256: {sha256_hash}")
    return manifest


if __name__ == "__main__":
    # Test execution for sample anchor record
    sample_apostille = "IMWM44AZGX6N6"
    sample_sec_code = "2013073817848"

    result = process_transnational_record(sample_apostille, sample_sec_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))
