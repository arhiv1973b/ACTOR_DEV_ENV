import os

def search_keys():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    print(f"--- [AUDIT] ПОИСК КЛЮЧЕЙ (DICOM/CT) ---")
    
    # Ключевые термины для поиска подлога
    keys = ['dicom', 'ct_scan', 'computed_tomography', 'tomography', 'scan_id']
    
    try:
        if not os.path.exists(registry_path):
            print(f"ОШИБКА: Файл {registry_path} не найден.")
            return

        with open(registry_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
        print("Сканирование манифеста...\n")
        for key in keys:
            count = content.count(key)
            print(f"Термин '{key}': найдено {count} упоминаний.")
            if count > 0:
                # Показать примерный контекст для первого вхождения
                idx = content.find(key)
                print(f"  Примерный контекст: ...{content[idx:idx+100]}...\n")

    except Exception as e:
        print(f"ОШИБКА: {e}")

if __name__ == "__main__":
    search_keys()
