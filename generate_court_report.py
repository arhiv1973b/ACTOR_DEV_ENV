import json
import os
from datetime import datetime

def generate_report():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    output_path = "final_evidence_report.md"

    if not os.path.exists(registry_path):
        print(f"[ERROR] Реестр {registry_path} не найден.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # Correctly access records under "evidence_nodes"
            entries = data.get("evidence_nodes", [])
        except json.JSONDecodeError:
            print("[ERROR] Ошибка декодирования JSON.")
            return

    with open(output_path, 'w', encoding='utf-8') as report:
        report.write("# ПРИЛОЖЕНИЕ К ХОДАТАЙСТВУ: ТЕХНИЧЕСКИЙ РЕЕСТР ДОКАЗАТЕЛЬСТВ\n\n")
        report.write(f"Дело: CASE-MACHERET-1997-2026\nСтатус: ЗАПЕЧАТАНА\nДата: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        report.write("| Файл | Дата | SHA256 (Хэш) |\n|---|---|---|\n")
        
        # Фильтруем записи по Марковой Галине
        found_count = 0
        for entry in entries:
            entry_str = json.dumps(entry)
            if "Marcova" in entry_str:
                file_name = entry.get('file', 'N/A')
                file_date = entry.get('date', 'N/A')
                file_hash = entry.get('hash', 'N/A')
                report.write(f"| {file_name} | {file_date} | {file_hash} |\n")
                found_count += 1

    print(f"[OK] Отчет сформирован: {output_path}")
    print(f"[INFO] Добавлено записей: {found_count}")

if __name__ == "__main__":
    generate_report()
