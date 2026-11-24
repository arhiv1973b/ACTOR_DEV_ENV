#!/usr/bin/env python3
import json
import re
import fitz
from pathlib import Path

# Пути к файлам
PDF_PATH = Path(r"H:\ACTOR_DEV_ENV\apostille_registry_working_18.signed.pdf")
JSON_PATH = Path(r"H:\ACTOR_DEV_ENV\exports\registry.json")

# Regex для извлечения (идентичен рабочему пайплайну)
CODE_RE = re.compile(r"apostileCode/([A-Z0-9]+)/securityCode/(\d+)", re.IGNORECASE)


def get_pdf_records():
    """Извлекает все записи напрямую из PDF."""
    records = set()
    doc = fitz.open(PDF_PATH)
    for page in doc:
        text = page.get_text()
        for match in CODE_RE.finditer(text):
            records.add((match.group(1).upper(), match.group(2)))
    doc.close()
    return records


def get_json_records():
    """Загружает записи из JSON."""
    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {(r["apostille"], r["security_code"]) for r in data}


def main():
    pdf_records = get_pdf_records()
    json_records = get_json_records()

    missing = pdf_records - json_records
    extra = json_records - pdf_records

    print(f"PDF records: {len(pdf_records)}")
    print(f"JSON records: {len(json_records)}")

    if missing:
        print(f"\nMissing ({len(missing)}):")
        for rec in sorted(list(missing)):
            print(f"  {rec[0]} / {rec[1]}")

    if extra:
        print(f"\nExtra ({len(extra)}):")
        for rec in sorted(list(extra)):
            print(f"  {rec[0]} / {rec[1]}")


if __name__ == "__main__":
    main()
