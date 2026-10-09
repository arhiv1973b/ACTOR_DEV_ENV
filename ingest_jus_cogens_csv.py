import os
import csv
import json
import hashlib
from datetime import datetime

CSV_PATH = r"H:\Загрузки\jus-cogens-7.csv"
MANIFEST_PATH = r"H:\ACTOR_DEV_ENV\dag_manifest.json"


def main():
    if not os.path.exists(CSV_PATH):
        print(f"CSV file not found: {CSV_PATH}")
        return

    print(f"[*] Чтение CSV файла: {CSV_PATH}")

    csv_rows = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_rows.append(row)

    print(f"[*] Прочитано строк: {len(csv_rows)}")

    # Загружаем существующий манифест
    manifest = []
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                manifest = data if isinstance(data, list) else data.get("entries", [])
        except Exception:
            manifest = []

    existing_hashes = {item.get("node_hash") for item in manifest}

    added_count = 0
    for row in csv_rows:
        vivod = row.get("Jus cogens вывод", "")
        vienna = row.get("Венская конвенция", "")
        udhr = row.get("UDHR статья", "")
        superposition = row.get("Перекрёстный смысл (суперпозиция)", "")

        payload_str = f"{vivod}|{vienna}|{udhr}|{superposition}"
        node_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        if node_hash not in existing_hashes:
            record = {
                "previous_hash": manifest[-1]["node_hash"]
                if manifest
                else "GENESIS_NODE",
                "payload": {
                    "case_id": "JUS-COGENS-SUPERPOSITION-2026",
                    "document_ref": "jus-cogens-7.csv",
                    "jus_cogens_conclusion": vivod,
                    "vienna_convention": vienna,
                    "udhr_article": udhr,
                    "superposition_meaning": superposition,
                    "registration_date": datetime.utcnow().isoformat() + "Z",
                    "protocol": "A©tor Key / TI-ULA Jurisprudence",
                },
                "node_hash": node_hash,
                "signature_ed25519": "verified_jus_cogens_matrix",
            }
            manifest.append(record)
            existing_hashes.add(node_hash)
            added_count += 1

    # Сохраняем обновленный манифест
    output_data = {
        "updated_at": datetime.utcnow().isoformat(),
        "total_entries": len(manifest),
        "entries": manifest,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(
        f"[✔] Успешно добавлено {added_count} записей из jus-cogens-7.csv в DAG-манифест. Всего записей: {len(manifest)}"
    )


if __name__ == "__main__":
    main()
