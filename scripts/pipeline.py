#!/usr/bin/env python3

import json
import hashlib
import requests
import time
import re

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader

PDF_FILE = "apostille_registry_working_18.signed.pdf"

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

MAX_STORAGE = 2147483648
MAX_WORKERS = 8
MAX_RETRIES = 5

URL_RE = re.compile(
    r"https://apostila\.gov\.md/"
    r"apostila/site/downloadApostila/"
    r"apostileCode/([A-Z0-9]+)/securityCode/(\d+)"
)


def extract_registry():
    reader = PdfReader(PDF_FILE)

    records = []

    for page in reader.pages:
        text = page.extract_text() or ""

        for apostille, security in URL_RE.findall(text):
            records.append(
                {
                    "apostille": apostille,
                    "security_code": security,
                    "url": f"https://apostila.gov.md/apostila/site/"
                    f"downloadApostila/apostileCode/"
                    f"{apostille}/securityCode/{security}",
                }
            )

    seen = set()
    unique = []

    for record in records:
        key = (record["apostille"], record["security_code"])

        if key not in seen:
            seen.add(key)

            unique.append(record)

    Path("registry.json").write_text(
        json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return unique


def verify_record(record):
    result = record.copy()

    result["status"] = 0
    result["sha256"] = None
    result["final_url"] = None
    result["size"] = 0
    result["error"] = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                record["url"], timeout=60, stream=True, allow_redirects=True
            )

            result["status"] = response.status_code
            result["final_url"] = response.url

            if response.status_code != 200:
                time.sleep(2**attempt)

                continue

            filename = DOWNLOAD_DIR / f"{record['apostille']}.pdf"

            sha = hashlib.sha256()

            with open(filename, "wb") as f:
                for chunk in response.iter_content(65536):
                    if chunk:
                        f.write(chunk)

                        sha.update(chunk)

            result["sha256"] = sha.hexdigest()

            result["size"] = filename.stat().st_size

            return result

        except Exception as ex:
            result["error"] = str(ex)

    return result


def current_storage():
    total = 0

    for f in DOWNLOAD_DIR.glob("*.pdf"):
        total += f.stat().st_size

    return total


def cleanup_fifo():
    while current_storage() > MAX_STORAGE:
        oldest = min(DOWNLOAD_DIR.glob("*.pdf"), key=lambda p: p.stat().st_mtime)

        print(f"DELETE: {oldest.name}")

        oldest.unlink()


def build_html(verified):
    rows = []

    for item in verified:
        rows.append(f"""
        <tr>
            <td>{item["apostille"]}</td>
            <td>{item["security_code"]}</td>
            <td>{item["status"]}</td>
            <td>{item["sha256"] or ""}</td>
            <td>
                <a href="{item["url"]}"
                   target="_blank">
                   Скачать
                </a>
            </td>
        </tr>
        """)

    html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<title>
Реестр апостилей
</title>

<style>
table {{
    width:100%;
    border-collapse:collapse;
}}

td,th {{
    border:1px solid #ccc;
    padding:8px;
}}
</style>

</head>

<body>

<h1>
Реестр апостилей
</h1>

<p>
# [⚖ A©tor Declaration]
</p>

<table>

<thead>

<tr>
<th>Апостиль</th>
<th>Security Code</th>
<th>HTTP</th>
<th>SHA256</th>
<th>Скачиваемые</th>
</tr>

</thead>

<tbody>

{"".join(rows)}

</tbody>

</table>

</body>
</html>
"""

    Path("index.html").write_text(html, encoding="utf-8")


def main():
    print("STEP 1: extract")

    records = extract_registry()

    print(f"records={len(records)}")

    print("STEP 2: verify")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        verified = list(pool.map(verify_record, records))

    Path("registry_verified.json").write_text(
        json.dumps(verified, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("STEP 3: cleanup")

    cleanup_fifo()

    print("STEP 4: build html")

    build_html(verified)

    print("DONE")


if __name__ == "__main__":
    main()
