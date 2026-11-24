#!/usr/bin/env python3
import json
import fitz
import re
import argparse
from pathlib import Path

# Паттерн для поиска пары: Апостиль (строка 1) -> Код безопасности (строка 2)
# В таблице они идут друг за другом
# Паттерн: Апостиль (обычно 12-15 символов) + Код безопасности (13 цифр)
TABLE_RE = re.compile(r"([A-Z0-9]{12,15})\s*\n\s*(\d{13,})")


def extract_from_pdf(pdf_path: Path):
    """Извлекает записи из PDF на основе табличного расположения."""
    records = set()
    doc = fitz.open(pdf_path)

    for page in doc:
        text = str(page.get_text("text") or "")

        # Поиск по табличному паттерну
        for match in TABLE_RE.finditer(text):
            records.add((match.group(1).upper(), match.group(2)))

    doc.close()
    return records


def get_from_json(json_path: Path):
    """Извлекает записи (apostille, security_code) из JSON."""
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {(item["apostille"], item["security_code"]) for item in data}


def main():
    parser = argparse.ArgumentParser(description="Точная сверка PDF и JSON реестра")
    parser.add_argument("pdf", help="Путь к PDF")
    parser.add_argument("json", help="Путь к JSON")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    json_path = Path(args.json)

    print(f"[*] Сверка {pdf_path.name} и {json_path.name}...")

    pdf_records = extract_from_pdf(pdf_path)
    json_records = get_from_json(json_path)

    missing = pdf_records - json_records
    extra = json_records - pdf_records

    print(f"PDF records: {len(pdf_records)}")
    print(f"JSON records: {len(json_records)}")

    if missing:
        print(f"\nMissing (in PDF, not in JSON): {len(missing)}")
        for rec in sorted(list(missing)):
            print(f"  {rec}")

    if extra:
        print(f"\nExtra (in JSON, not in PDF): {len(extra)}")
        for rec in sorted(list(extra)):
            print(f"  {rec}")

    if not missing and not extra:
        print("\n[OK] Сверка успешна: записи идентичны.")


if __name__ == "__main__":
    main()
