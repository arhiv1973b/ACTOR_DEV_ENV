import json
import os

def extract_evidence():
    registry_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\pdfs_mirror\evidence_registry.json"
    print(f"--- [AUDIT] КРОСС-ПРОВЕРКА ДАТ 09.01.2022 и 14.03.2022 ---")
    
    if not os.path.exists(registry_path):
        print(f"ОШИБКА: Файл {registry_path} не найден.")
        return

    # Вариации форматов дат для надежного поиска
    target_dates = ['09.01.2022', '14.03.2022', '2022-01-09', '2022-03-14', '09_01_2022', '14_03_2022']
    
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        print("Сканирование 1.8 MB манифеста...\n")
        
        match_count = 0
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(d in line_lower for d in target_dates):
                match_count += 1
                print(f"[УЗЕЛ ИСТИНЫ | Строка {i}]")
                # Извлекаем блок контекста (предыдущие 3 и следующие 6 строк для захвата хэшей и путей)
                start = max(0, i - 3)
                end = min(len(lines), i + 7)
                for j in range(start, end):
                    prefix = " >> " if j == i else "    "
                    print(f"{prefix}{lines[j].rstrip()}")
                print("-" * 60)
                
            if match_count >= 20:
                print("\n[ВНИМАНИЕ] Достигнут лимит вывода (20 записей).")
                break
                
        if match_count == 0:
            print("Точных совпадений по датам не найдено. Требуется расширенный поиск по ключевым словам (DICOM, CT).")
        else:
            print(f"\nИзвлечение завершено. Найдено записей: {match_count}")
            
    except Exception as e:
        print(f"ОШИБКА ИЗВЛЕЧЕНИЯ: {e}")

if __name__ == "__main__":
    extract_evidence()
