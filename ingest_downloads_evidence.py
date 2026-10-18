import os
import hashlib
import json
from datetime import datetime, timezone

files = [
    r"H:\Загрузки\25 _7.jpg",
    r"H:\Загрузки\25 и четверть _7.pdf",
    r"H:\Загрузки\25 и четверть _8.jpg",
    r"H:\Загрузки\25 мл 2_3.pdf",
    r"H:\Загрузки\25 мл 2_4.jpg",
    r"H:\Загрузки\1500 $ 2_1.pdf",
    r"H:\Загрузки\20260716140348300_3.pdf",
    r"H:\Загрузки\Atunci!! Constituționale Sesizare.pdf",
    r"H:\Загрузки\Aviza.pdf",
    r"H:\Загрузки\We Have Received Your Message_6.подписан 2.pdf",
    r"H:\Загрузки\Кебеш в отношении кражи_1.pdf",
    r"H:\Загрузки\Кража средстств выделенных по личному распоряжению Президента США Мистер Дональда Трампа_2.pdf",
    r"H:\Загрузки\Фамилия_5.signed.signed.signed.signed.pdf",
]

results = []
for path in files:
    entry = {"path": path, "filename": os.path.basename(path)}
    if os.path.exists(path):
        sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    sha256.update(chunk)
            entry["sha256"] = sha256.hexdigest()
            entry["size_bytes"] = os.path.getsize(path)
            entry["status"] = "verified_exists"
        except Exception as e:
            entry["sha256"] = f"ERROR: {str(e)}"
            entry["status"] = "read_error"
    else:
        entry["sha256"] = "FILE_NOT_FOUND"
        entry["status"] = "missing"
    results.append(entry)

manifest = {
    "manifest_schema": "TI-ULA/1.0",
    "project_id": "CASE-MACHERET-1997-2026",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "evidence_items": results,
}

output_path = r"H:\ACTOR_DEV_ENV\downloads_evidence_manifest_07102026.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(
    f"Successfully processed {len(results)} evidence items. Manifest saved to {output_path}"
)
