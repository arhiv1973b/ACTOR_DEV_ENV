#!/usr/bin/env python3
"""Проверка целостности PDF-ссылок апостилей. Помечает пустые/битые."""

import json
import urllib.request
import ssl
from pathlib import Path

MANIFEST = Path("manifest.json")
BASE = "https://arhiv1973b.github.io/apostille-archive-english/"
THRESHOLD = 1024  # < 1 KB = empty/tampered

ctx = ssl.create_default_context()


def check(url: str) -> dict:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, context=ctx, timeout=15) as r:
            cl = int(r.headers.get("Content-Length", 0) or 0)
            ct = r.headers.get("Content-Type", "")
            return {
                "ok": cl >= THRESHOLD and "pdf" in ct.lower(),
                "size": cl,
                "content_type": ct,
                "status_code": r.status,
            }
    except Exception as e:
        return {"ok": False, "size": 0, "error": str(e)}


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = []
    for rec in data["records"]:
        url = BASE + rec["filename"]
        res = check(url)
        status = "ok" if res["ok"] else "tampered/empty"
        if rec.get("status") == "defective_signature":
            status = "defective_signature + " + status
        print(
            f"{rec['id']:3} | {rec['code']:20} | {status:30} | {res.get('size', 0):>8} bytes"
        )
        results.append({**rec, "check": res, "final_status": status})

    out = Path("check_report.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nОтчёт сохранён: {out}")


if __name__ == "__main__":
    main()
