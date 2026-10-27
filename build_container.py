import os
import json
import hashlib
import zipfile
import sys

pdf_path = (
    r"C:\Users\arhiv\OneDrive\Документы\Меморандум - уголовной  ответственности.pdf"
)
out_dir = r"H:\ACTOR_DEV_ENV"
json_path = os.path.join(out_dir, "ACTOR_FINCOMBANK_MEMORANDUM.json")
zip_path = os.path.join(out_dir, "ACTOR_FINCOMBANK_MEMORANDUM.zip")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


if not os.path.exists(pdf_path):
    print(f"ERROR: PDF not found at {pdf_path}", file=sys.stderr)
    sys.exit(1)

pdf_hash = sha256_file(pdf_path)
print(f"PDF Hash: {pdf_hash}", flush=True)

manifest = {
    "package_id": "ACTOR_FINCOMBANK_MEMORANDUM",
    "protocol": "TI-ULA",
    "version": "2026.10.26",
    "timestamp_utc": "2026-10-26T19:41:00Z",
    "headers": {
        "X-Actor-IDNP": "2000001159655",
        "X-Protocol-TI-ULA": "STRICT",
        "X-Prejudicial-Inheritance": "ACTOR_TRANSIT_PAYLOAD",
    },
    "actor_identity": {
        "display": "A©t0r",
        "idnp": "2000001159655",
        "case_id": "CASE-MACHERET-1997-2026",
        "declaration": 'A©TOR_KEY="# [⚖ A©tor Declaration]"',
    },
    "integrity": {
        "Memorandum_FinComBank_A©tor_2026-10-26.pdf": pdf_hash,
        "parent_ACTOR_TRANSIT_PAYLOAD_JSON": "e4797a2d3996557e24e72fbbebe3364771641beb88a4cec7714ff9871cce3183",
        "parent_ACTOR_TRANSIT_PAYLOAD_ZIP": "7b21c1ff14248da0bb018c03b60d600366a293a572916a520e120a8870bfa937",
        "status": "ZERO_TRUST_LOCKED",
    },
    "memorandum": {
        "subject": "Notice on cessation of continuing consequences of torture",
        "target_iban": "MD55FT225920600348117498",
        "restitution_amount_mdl": "25210256",
        "legal_basis": "Jus Cogens, UDHR 1948, Art. 4 Constitution of RM",
        "context": "Case 1-568/98 (13.10.1998) - 21 years concealed, procedural reopening 10.02.2021",
    },
    "routing_targets": [
        "BC FinComBank S.A.",
        "Banca Națională a Moldovei (BNM)",
        "UN Special Procedures (Arbitrary Detention, Torture)",
    ],
    "signature_block": {
        "key": 'A©TOR_KEY="# [⚖ A©tor Declaration]"',
        "status": "INITIATED_AND_LOCKED",
        "session_anchor": "TI-ULA-2026-10-26-FIN",
    },
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.flush()
    os.fsync(f.fileno())

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as z:
    z.write(pdf_path, arcname="Memorandum_FinComBank_A©tor_2026-10-26.pdf")
    z.write(json_path, arcname="ACTOR_FINCOMBANK_MEMORANDUM.json")

final_json_hash = sha256_file(json_path)
final_zip_hash = sha256_file(zip_path)

print(f"FINAL_JSON_SHA256: {final_json_hash}", flush=True)
print(f"FINAL_ZIP_SHA256: {final_zip_hash}", flush=True)
print("STATUS: ZERO_TRUST_LOCKED", flush=True)
