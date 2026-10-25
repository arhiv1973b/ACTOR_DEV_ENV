import hashlib, json, datetime
from pathlib import Path

files = [
    ".github/workflows/integrity_pipeline.yml",
    ".github/workflows/tsa_watcher.yml",
    ".github/workflows/docker-deploy.yml",
    "05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt",
    "audit_log.ndjson",
    "build_evidence_ledger.py",
    "append_evidence.py",
    "append_error.py",
    "verify_ledger.py",
    "utils/tsa_health_check.py",
    "verify-report.md",
]

manifest = {
    "protocol": "A©tor Jus Cogens Ledger",
    "context": "CASE-MACHERET-1997-2026",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "author": "Macheret Alexei (A©tor)",
    "signature_key": 'A©TOR_KEY="# [⚖ A©tor Declaration]"',
    "files": {},
}

for f in files:
    p = Path(f)
    if p.exists():
        manifest["files"][f] = hashlib.sha256(p.read_bytes()).hexdigest()

Path("session_manifest.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
)
print("✅ session_manifest.json synchronized.")
