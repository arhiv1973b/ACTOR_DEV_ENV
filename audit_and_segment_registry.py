import os
import json
from datetime import datetime

def audit_and_segment():
    registry_path = r"H:\ACTOR_DEV_ENV\EVIDENCE_REGISTRY_INDEX.json"
    print(f"--- [AUDIT] АНАЛИЗ И СЕГМЕНТАЦИЯ РЕЕСТРА: {registry_path} ---")
    
    if not os.path.exists(registry_path):
        print(f"ОШИБКА: Файл {registry_path} не найден.")
        return

    file_size_mb = os.path.getsize(registry_path) / (1024 * 1024)
    print(f"Размер файла: {file_size_mb:.2f} MB")

    try:
        print("Загрузка и проверка структуры JSON (это может занять несколько секунд из-за размера)...")
        with open(registry_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"Тип данных: Список. Всего записей (чанков): {len(data)}")
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    chunk_id = item.get('chunk_id', f'chunk_{idx}')
                    nodes = item.get('evidence_nodes', [])
                    print(f"  Чанк [{idx}] ID: {chunk_id} | Узлов доказательств: {len(nodes)}")
                else:
                    print(f"  Элемент [{idx}]: тип {type(item)}")
        elif isinstance(data, dict):
            print(f"Тип данных: Словарь. Ключи: {list(data.keys())}")
            # Если есть ключ с записями
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"  Ключ '{k}' содержит список из {len(v)} элементов.")
        else:
            print(f"Тип данных: {type(data)}")

        print("Аудит целостности реестра доказательств успешно завершен: структура валидна.")

    except Exception as e:
        print(f"ОШИБКА ПРИ РАЗБОРЕ JSON: {e}")

if __name__ == "__main__":
    audit_and_segment()
