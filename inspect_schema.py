import json
import os

def inspect_schema():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"[ERROR] Реестр {registry_path} не найден.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            entries = data if isinstance(data, list) else data.get("entries", [])
            if entries:
                print("--- [AUDIT] СТРУКТУРА ЗАПИСИ (ПЕРВАЯ) ---")
                print(json.dumps(entries[0], indent=2, ensure_ascii=False))
            else:
                print("[INFO] Реестр пуст.")
        except json.JSONDecodeError:
            print("[ERROR] Ошибка декодирования JSON.")

if __name__ == "__main__":
    inspect_schema()
