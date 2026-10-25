import socket
import ssl
import time
import os
import json
import datetime
import hashlib
from pathlib import Path
from urllib.parse import urlparse

TSA_URLS = [
    "https://freetsa.org/tsr",
    "http://timestamp.apple.com/ts01",
    "http://timestamp.digicert.com",
]


def audit_tsa_node(url):
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    cert_expiry = "N/A (HTTP)"
    if parsed.scheme == "https":
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    cert_expiry = cert.get("notAfter", "N/A")
                    if ssl.cert_time_to_seconds(cert_expiry) < time.time():
                        return None
        except Exception:
            return None

    try:
        start = time.time()
        with socket.create_connection((host, port), timeout=5):
            latency = time.time() - start
            return (latency, cert_expiry)
    except Exception:
        return None


def log_tsa_audit_to_ledger(active_url, latency, cert_expiry):
    ledger_path = Path("audit_log.ndjson")

    prev_hash = "GENESIS_BLOCK_CASE_MACHERET_1997_2026"
    index = 1
    if ledger_path.exists():
        lines = [
            l.strip()
            for l in ledger_path.read_text(encoding="utf-8").splitlines()
            if l.strip()
        ]
        if lines:
            try:
                last_record = json.loads(lines[-1])
                prev_hash = last_record.get("block_hash", prev_hash)
                index = last_record.get("index", 0) + 1
            except Exception:
                pass

    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    record = {
        "index": index,
        "previous_block_hash": prev_hash,
        "timestamp": timestamp,
        "author": "A©tor System Watcher",
        "email": "alexeimaceret7@gmail.com",
        "subject": f"TSA Health Audit: Active Node {active_url}",
        "metrics": {
            "active_tsa_url": active_url,
            "latency_seconds": round(latency, 4),
            "certificate_not_after": cert_expiry,
        },
        "protocol": "A©tor Jus Cogens Ledger",
    }

    record_str = json.dumps(record, sort_keys=True)
    block_hash = hashlib.sha256(record_str.encode("utf-8")).hexdigest()
    record["block_hash"] = block_hash

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")

    print(
        f"✅ TSA Audit successfully appended to {ledger_path} (Block Hash: {block_hash[:12]}...)"
    )


if __name__ == "__main__":
    print("=== Executing A©t0r Protocol: TSA Node Audit & Ledger Integration ===")
    pool = []
    for u in TSA_URLS:
        result = audit_tsa_node(u)
        if result is not None:
            latency, not_after = result
            pool.append((latency, u, not_after))

    if not pool:
        print("❌ CRITICAL: All TSA nodes unreachable. Jus Cogens linearity at risk.")
        exit(1)

    pool.sort(key=lambda x: x[0])
    best_latency, best_url, best_expiry = pool[0]

    log_tsa_audit_to_ledger(best_url, best_latency, best_expiry)

    ordered_urls = " ".join([u for _, u, _ in pool])
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a") as f:
            f.write(f"TSA_POOL={ordered_urls}\n")

    print(f"✅ TSA Pool prioritized by latency: {ordered_urls}")
