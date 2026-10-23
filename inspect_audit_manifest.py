import os

def inspect_manifest():
    path = r"H:\ACTOR_DEV_ENV\apostille-mirror\A©tor_FORENSIC_AUDIT_MANIFEST_V4_4.md"
    print(f"--- [AUDIT] ЧТЕНИЕ МАНИФЕСТА АУДИТА ---")
    
    try:
        if not os.path.exists(path):
            print(f"ОШИБКА: Файл {path} не найден.")
            return

        with open(path, 'r', encoding='utf-8') as f:
            print(f.read(2000))
            
    except Exception as e:
        print(f"ОШИБКА ЧТЕНИЯ: {e}")

if __name__ == "__main__":
    inspect_manifest()
