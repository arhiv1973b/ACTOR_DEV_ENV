# send_forensic_report.py
import os
import hmac
import hashlib
import requests

REPORT_FILE = "artifacts/reabilitare/forensic_capture_ledger.json"
SECRET_KEY = b"supersecretkey"

webhook_url = os.getenv("FORENSIC_WEBHOOK_URL")
if not webhook_url:
    raise RuntimeError("FORENSIC_WEBHOOK_URL not set")

bearer_token = os.getenv("FORENSIC_BEARER_TOKEN")

with open(REPORT_FILE, "rb") as f:
    body = f.read()

signature = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()

payload = {"report": body.decode("utf-8"), "signature": signature}

headers = {"Content-Type": "application/json"}
if bearer_token:
    headers["Authorization"] = f"Bearer {bearer_token}"

resp = requests.post(webhook_url, json=payload, headers=headers)
resp.raise_for_status()
print("[OK] Forensic report sent successfully with HMAC signature and Bearer auth.")
