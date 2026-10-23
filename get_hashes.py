import json

def get_hashes():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("--- [AUDIT] ИЗВЛЕЧЕНИЕ ХЭШЕЙ ---")
        found = False
        # Предполагаем, что registry может быть списком или словарем с ключом "entries"
        entries = data if isinstance(data, list) else data.get("entries", [])
        
        for entry in entries:
            # Преобразуем entry в строку для поиска
            entry_str = json.dumps(entry)
            if "Alpha" in entry_str or "Beta" in entry_str:
                found = True
                print(f"СЕРИЯ: {entry.get('series_name', 'Unknown')}")
                print(f"ХЭШ SHA256: {entry.get('sha256', 'NOT_FOUND')}")
                print(f"ПУТЬ: {entry.get('file_path', 'NOT_FOUND')}\n")
        
        if not found:
            print("Записи для серий Alpha или Beta не найдены в структуре реестра.")
            
    except Exception as e:
        print(f"Ошибка чтения реестра: {e}")

if __name__ == "__main__":
    get_hashes()
