import json
import os

def quick_audit():
    print("--- [AUDIT] ПРЯМОЙ АНАЛИЗ ---")
    try:
        # Анализ меморандума
        memo_path = r"H:\ACTOR_DEV_ENV\apostille-mirror\CASE_MACHERET_FINAL_MEMORANDUM.md"
        if os.path.exists(memo_path):
            with open(memo_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Поиск ключевых строк
                status_line = [line for line in content.split('\n') if "статус" in line.lower()]
                print(f"СТАТУС: {status_line[0] if status_line else 'Не определен'}")
        else:
            print(f"Файл {memo_path} не найден.")
            
        # Анализ даты
        integrity_path = r"H:\ACTOR_DEV_ENV\integrity.json"
        if os.path.exists(integrity_path):
            with open(integrity_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"DATE: {data.get('updated', 'Не найдена')}")
        else:
            print(f"Файл {integrity_path} не найден.")
    except Exception as e:
        print(f"ОШИБКА АНАЛИЗА: {e}")

if __name__ == "__main__":
    quick_audit()
