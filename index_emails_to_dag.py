#!/usr/bin/env python3
import os
import hashlib
import json
import datetime

EMAIL_DIR = r"H:\ACTOR_DEV_ENV\inbox\emails"
OUTPUT_REGISTRY = r"H:\ACTOR_DEV_ENV\maceret-case-evidence\email_evidence_registry.json"
ANCHOR_ID = "90655f14"


def hash_file(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return str(e)


def build_registry():
    # Use UTC timezone safely compatible across python versions
    try:
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    except AttributeError:
        now_str = datetime.datetime.utcnow().isoformat() + "+00:00"

    print(f"[{now_str}] Запуск сканирования почтового архива...")
    registry = {
        "registry_type": "EMAIL_FORENSIC_INDEX",
        "case_id": "CASE-MACHERET-1997-2026",
        "financial_anchor_link": ANCHOR_ID,
        "legal_basis": "UDHR Art. 3, Art. 17.2 (Proof of non-rehabilitation)",
        "emails": [],
    }

    if not os.path.exists(EMAIL_DIR):
        print(f"Директория {EMAIL_DIR} не найдена. Создаем ее...")
        os.makedirs(EMAIL_DIR, exist_ok=True)

    count = 0
    for root, _, files in os.walk(EMAIL_DIR):
        for file in files:
            filepath = os.path.join(root, file)
            file_hash = hash_file(filepath)
            registry["emails"].append(
                {
                    "filename": file,
                    "sha256": file_hash,
                    "status": "LOCKED",
                    "relation_to_anchor": "CONTINUING_VIOLATION_EVIDENCE",
                }
            )
            count += 1

    with open(OUTPUT_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)

    print(f"[+] Проиндексировано писем/вложений: {count}")
    print(f"[+] Реестр сохранен: {OUTPUT_REGISTRY}")


if __name__ == "__main__":
    build_registry()
