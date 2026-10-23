import os
import fnmatch
from datetime import datetime

def scan_for_manifest():
    search_dir = r"H:\ACTOR_DEV_ENV"
    print(f"--- [AUDIT] СКАНИРОВАНИЕ РЕЕСТРОВ CAS В {search_dir} ---")
    
    if not os.path.exists(search_dir):
        print(f"ОШИБКА: Директория {search_dir} не найдена.")
        return

    # Ключевые паттерны для поиска манифестов и реестров
    patterns = [
        '*manifest*.json', '*registry*.json', '*hash*.json', 
        '*cas*.json', '*index*.json', '*.csv', '*evidence*.md'
    ]
    
    found_files = []
    
    for root, dirs, files in os.walk(search_dir):
        # Пропускаем технические папки git и виртуальные окружения
        if '.git' in root or 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if any(fnmatch.fnmatch(file.lower(), p) for p in patterns):
                full_path = os.path.join(root, file)
                try:
                    size_kb = os.path.getsize(full_path) / 1024
                    mtime = os.path.getmtime(full_path)
                    # Фильтруем пустые файлы
                    if size_kb > 0:
                        found_files.append((full_path, size_kb, mtime))
                except Exception as e:
                    pass

    # Сортируем по размеру по убыванию (манифест на 4010+ узлов должен быть большим)
    found_files.sort(key=lambda x: x[1], reverse=True)

    if found_files:
        print(f"\nНАЙДЕНО ПОТЕНЦИАЛЬНЫХ РЕЕСТРОВ: {len(found_files)}")
        print("ТОП-10 КАНДИДАТОВ (по размеру):\n")
        for path, size, mtime in found_files[:10]:
            date_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            # Оставляем только относительный путь для удобства чтения
            rel_path = os.path.relpath(path, search_dir)
            print(f" > {rel_path}")
            print(f"   Размер: {size:.2f} KB | Изменен: {date_str}\n")
    else:
        print("\nПотенциальные реестры (manifest/registry/hash/cas) не найдены.")

if __name__ == "__main__":
    scan_for_manifest()
