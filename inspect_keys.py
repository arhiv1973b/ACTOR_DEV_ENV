import json
import os

def inspect_keys():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"[ERROR] Реестр {registry_path} не найден.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            print("--- [AUDIT] КЛЮЧИ РЕЕСТРА ---")
            print(list(data.keys()))
        except json.JSONDecodeError:
            print("[ERROR] Ошибка декодирования JSON.")

if __name__ == "__main__":
    inspect_keys()
