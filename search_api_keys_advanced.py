import os
import json
from pathlib import Path

root_dir = r"F:\Мой диск"
out_path = Path(r"H:\ACTOR_DEV_ENV\api_search_report.txt")
os.makedirs(out_path.parent, exist_ok=True)

target_names = {"credentials.json", "token.json"}
found_files = []

print(f"[*] Сканирование диска {root_dir} на наличие учетных данных Google API...")

for root, dirs, files in os.walk(root_dir):
    for file in files:
        lf = file.lower()
        if (
            lf in target_names
            or "client_secret" in lf
            or "oauth" in lf
            or "drive" in lf
            and "api" in lf
            or (
                file.endswith(".json")
                and ("client_id" in file.lower() or "cred" in file.lower())
            )
        ):
            fp = os.path.join(root, file)
            found_files.append(fp)

# Также дополнительно проверим .json файлы на наличие ключевых полей внутри
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".json"):
            fp = os.path.join(root, file)
            if fp not in found_files:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Проверка на installed / web или service_account
                        if isinstance(data, dict):
                            if (
                                "installed" in data
                                or "web" in data
                                or data.get("type") == "service_account"
                            ):
                                found_files.append(fp)
                except Exception:
                    pass

with open(out_path, "w", encoding="utf-8") as out:
    out.write(
        "=== ОТЧЕТ ПО ПОИСКУ GOOGLE API КЛЮЧЕЙ И ТОКЕНОВ (CASE-MACHERET-1997-2026) ===\n\n"
    )
    if found_files:
        for fp in found_files:
            try:
                size = os.path.getsize(fp)
                out.write(f"📁 НАЙДЕНО: {fp} | Размер: {size} байт\n")
            except Exception:
                out.write(f"📁 НАЙДЕНО: {fp} | Размер: N/A\n")
            out.flush()
    else:
        out.write(
            "❌ На диске F:\\Мой диск целевых файлов конфигурации не обнаружено.\n"
        )
    out.flush()

print(f"✅ Отчет успешно сохранен в: {out_path}")
