import os
import shutil
from pathlib import Path

# КОНФИГУРАЦИЯ
REPO_ROOT = Path("H:/ACTOR_DEV_ENV/apostille-archive-english")
SOURCE_DIR = Path("C:/Temp/apostille_source") # Укажите здесь путь, где лежат настоящие PDF
THRESHOLD = 1024 # 1 KB

def recover():
    count = 0
    for pdf_file in REPO_ROOT.glob("apostille_*.pdf"):
        if pdf_file.stat().st_size < THRESHOLD:
            print(f"[!] Обнаружена заглушка: {pdf_file.name} ({pdf_file.stat().st_size} bytes)")
            source_file = SOURCE_DIR / pdf_file.name
            if source_file.exists():
                shutil.copy2(source_file, pdf_file)
                print(f"[+] Восстановлено из источника: {pdf_file.name}")
                count += 1
            else:
                print(f"[-] Ошибка: Файл не найден в источнике: {source_file}")
    print(f"\nВсего восстановлено файлов: {count}")

if __name__ == "__main__":
    recover()
