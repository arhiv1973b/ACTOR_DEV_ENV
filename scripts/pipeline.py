#!/usr/bin/env python3

import json
import hashlib
import requests
import time
import re
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader

# Configuration
PDF_FILE = "apostille_registry_working_18.signed.pdf"
DOWNLOADS = Path("downloads")
REPORTS = Path("reports")
DOCS = Path("docs")
OUTPUT = Path("output")

DOWNLOADS.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

MAX_STORAGE = 2147483648  # 2 GB
MAX_WORKERS = 8
MAX_RETRIES = 5
REQUEST_TIMEOUT = 60

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

URL_RE = re.compile(
    r"https://apostila\.gov\.md/"
    r"apostila/site/downloadApostila/"
    r"apostileCode/([A-Z0-9]+)/securityCode/(\d+)"
)


def extract_registry():
    reader = PdfReader(PDF_FILE)
    records = []
    num = 1
    for page in reader.pages:
        text = page.extract_text() or ""
        for apostille, security in URL_RE.findall(text):
            records.append(
                {
                    "num": num,
                    "apostille": apostille,
                    "security_code": security,
                    "url": f"https://apostila.gov.md/apostila/site/downloadApostila/apostileCode/{apostille}/securityCode/{security}",
                }
            )
            num += 1

    # Deduplicate
    seen = set()
    unique = []
    for record in records:
        key = (record["apostille"], record["security_code"])
        if key not in seen:
            seen.add(key)
            unique.append(record)
    return unique


def verify_record(record):
    result = record.copy()
    result.update(
        {"status": 0, "sha256": None, "size": 0, "final_url": None, "error": None}
    )

    try:
        response = requests.get(
            record["url"], timeout=REQUEST_TIMEOUT, stream=True, allow_redirects=True
        )
        result["status"] = response.status_code
        result["final_url"] = response.url

        if response.status_code != 200:
            return result

        filename = DOWNLOADS / f"{record['apostille']}.pdf"
        sha = hashlib.sha256()

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
                    sha.update(chunk)

        result["sha256"] = sha.hexdigest()
        result["size"] = filename.stat().st_size

    except Exception as ex:
        result["error"] = str(ex)
        with open(REPORTS / "anomalies.jsonl", "a", encoding="utf-8") as log:
            log.write(json.dumps(result, ensure_ascii=False) + "\n")

    return result


def current_storage():
    return sum(f.stat().st_size for f in DOWNLOADS.glob("*.pdf"))


def cleanup_fifo():
    while current_storage() > MAX_STORAGE:
        pdfs = list(DOWNLOADS.glob("*.pdf"))
        if not pdfs:
            break
        oldest = min(pdfs, key=lambda p: p.stat().st_mtime)
        logging.info("DELETE %s", oldest.name)
        oldest.unlink()


def build_page(records):
    rows = []
    for item in records:
        rows.append(f"""
        <tr>
            <td>{item["num"]}</td>
            <td>{item["apostille"]}</td>
            <td>{item["security_code"]}</td>
            <td>{item["status"]}</td>
            <td>{item["sha256"] or ""}</td>
            <td><a href="{item["url"]}" target="_blank" rel="noopener noreferrer">Download</a></td>
        </tr>
        """)
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Apostille Archive</title>
<style>body{{font-family:Arial,sans-serif;margin:20px;}}table{{width:100%;border-collapse:collapse;}}th{{background:#244a86;color:white;}}td,th{{border:1px solid #d0d0d0;padding:8px;}}</style>
</head>
<body>
<h1>Apostille Archive</h1>
<p># [⚖ A©tor Declaration]</p>
<table>
<thead><tr><th>No</th><th>Apostille</th><th>Security Code</th><th>HTTP</th><th>SHA256</th><th>Download</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
</body>
</html>"""
    (DOCS / "apostille_archive_english.html").write_text(html, encoding="utf-8")


def build_info(records):
    online = len([r for r in records if r["status"] == 200])
    info = {
        "records": len(records),
        "online": online,
        "offline": len(records) - online,
        "storage": current_storage(),
    }
    (OUTPUT / "build_info.json").write_text(
        json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main():
    logging.info("START PIPELINE")
    if not Path(PDF_FILE).exists():
        logging.error("PDF not found: %s", PDF_FILE)
        return

    records = extract_registry()
    logging.info("EXTRACTED %s RECORDS", len(records))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        verified = list(pool.map(verify_record, records))

    (OUTPUT / "registry_verified.json").write_text(
        json.dumps(verified, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    cleanup_fifo()
    build_page(verified)
    build_info(verified)
    logging.info("PIPELINE FINISHED")


if __name__ == "__main__":
    main()
