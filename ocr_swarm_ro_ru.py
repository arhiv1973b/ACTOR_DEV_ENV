# ocr_swarm_ro_ru.py
# A©tor_KEY="# [⚖ A©tor Declaration]"
# Swarm OCR: Romanian + Russian via public catalogs / public OCR APIs.
# Raw output keeps defects. Fingerprint stays in ocr_zero_weight_bridge.
#
# Workers:
#   1) local Tesseract  -l ron+rus+eng  (public tessdata models)
#   2) OCR.space Engine 3 language=auto (public HTTPS API; rus + ron in 200+ set)
# Do not harvest private keys. Optional env OCRSPACE_API_KEY; else documented test key.

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from ocr_zero_weight_bridge import process_ocr_to_udhr_pointer

TESSDATA_FAST = "https://github.com/tesseract-ocr/tessdata_fast/raw/main"
OCRSPACE_URL = "https://api.ocr.space/parse/image"
OCRSPACE_TEST_KEY = "helloworld"


def _tess_bin():
    win = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.name == "nt" and os.path.isfile(win):
        return win
    return shutil.which("tesseract")


def worker_tesseract(image, langs, psm):
    exe = _tess_bin()
    if not exe:
        return {"worker": "tesseract", "ok": False, "error": "tesseract binary missing"}
    cmd = [exe, image, "stdout", "-l", langs, "--oem", "1", "--psm", psm]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
        raw = proc.stdout.decode("utf-8", errors="replace")
        err = proc.stderr.decode("utf-8", errors="replace")
        if proc.returncode != 0 and not raw.strip():
            return {"worker": "tesseract", "ok": False, "error": err[-400:], "lang": langs}
        return {"worker": "tesseract", "ok": True, "lang": langs, "raw": raw, "stderr_tail": err[-200:]}
    except Exception as e:
        return {"worker": "tesseract", "ok": False, "error": str(e)}


def worker_ocrspace(image):
    key = os.environ.get("OCRSPACE_API_KEY") or OCRSPACE_TEST_KEY
    boundary = "----TIULAOCR7"
    data = Path(image).read_bytes()
    name = Path(image).name
    mime = "image/png" if name.lower().endswith(".png") else "image/jpeg"
    parts = []

    def field(k, v):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8")
        )

    field("apikey", key)
    field("language", "auto")
    field("OCREngine", "3")
    field("isOverlayRequired", "false")
    parts.append(
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\n"
            f"Content-Type: {mime}\r\n\r\n"
        ).encode("utf-8")
        + data
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    req = urllib.request.Request(
        OCRSPACE_URL,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"worker": "ocrspace", "ok": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"worker": "ocrspace", "ok": False, "error": str(e)}

    if payload.get("IsErroredOnProcessing"):
        return {"worker": "ocrspace", "ok": False, "error": payload.get("ErrorMessage")}
    parsed = payload.get("ParsedResults") or []
    raw = "\n".join(p.get("ParsedText") or "" for p in parsed)
    return {
        "worker": "ocrspace",
        "ok": bool(raw.strip()),
        "lang": "auto(engine3)",
        "raw": raw,
        "key_mode": "env" if os.environ.get("OCRSPACE_API_KEY") else "public_test",
    }


def pick_raw(results):
    ok = [r for r in results if r.get("ok") and (r.get("raw") or "").strip()]
    if not ok:
        bits = [f"{r.get('worker')}:{r.get('error')}" for r in results]
        raise SystemExit("swarm miss: " + " | ".join(bits))
    best = max(ok, key=lambda r: len(r.get("raw") or ""))
    return best["raw"], best["worker"]


def main():
    p = argparse.ArgumentParser(description="RO+RU OCR swarm to defect fingerprint")
    p.add_argument("--image", required=True)
    p.add_argument("--drive-link", required=True)
    p.add_argument("--output-name", required=True)
    p.add_argument("--psm", default="6")
    p.add_argument("--langs", default="ron+rus+eng")
    p.add_argument("--skip-cloud", action="store_true")
    args = p.parse_args()

    swarm = [worker_tesseract(args.image, args.langs, args.psm)]
    if not args.skip_cloud:
        swarm.append(worker_ocrspace(args.image))

    raw, winner = pick_raw(swarm)
    raw_dir = Path("🇻️_EVIDENCE") / "OCR_TEXT_LAYER" / "RAW_WITH_ERRORS"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{args.output_name}_raw.txt"
    raw_path.write_text(raw, encoding="utf-8")

    log_path = raw_dir / f"{args.output_name}_swarm.json"
    safe_swarm = []
    for r in swarm:
        item = {k: v for k, v in r.items() if k != "raw"}
        item["raw_chars"] = len(r.get("raw") or "")
        safe_swarm.append(item)
    log_path.write_text(
        json.dumps({"winner": winner, "workers": safe_swarm}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[+] swarm winner={winner} raw={raw_path}")
    process_ocr_to_udhr_pointer(args.drive_link, str(raw_path), args.output_name, target_lang="ro")


if __name__ == "__main__":
    main()
