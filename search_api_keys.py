import os
from pathlib import Path

root_dir = r"F:\Мой диск"
out_path = Path(r"H:\ACTOR_DEV_ENV\api_search_report.txt")
os.makedirs(out_path.parent, exist_ok=True)

target_names = {"credentials.json", "token.json"}
found_files = []

print(f"🔍 Сканирование диска {root_dir} на наличие учетных данных Google API...")

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if (
            file.lower() in target_names
            or "client_secret" in file.lower()
            or "oauth" in file.lower()
        ):
            fp = os.path.join(root, file)
            found_files.append(fp)

with open(out_path, "w", encoding="utf-8") as out:
    out.write("=== ОТЧЕТ ПО ПОИСКУ GOOGLE API КЛЮЧЕЙ И ТОКЕНОВ ===\n\n")
    if found_files:
        for fp in found_files:
            out.write(f"📁 НАЙДЕНО: {fp}\n")
    else:
        out.write(
            "❌ На диске F:\\Мой диск целевых файлов конфигурации не обнаружено.\n"
        )

print(f"✅ Отчет успешно сохранен в: {out_path}")
