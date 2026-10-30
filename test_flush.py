import os
from pathlib import Path

target_dir = Path(r"H:\ACTOR_DEV_ENV")
target_dir.mkdir(parents=True, exist_ok=True)

file_path = target_dir / "found_creds.txt"

# Безопасная запись с принудительным сбросом буфера
with open(file_path, "w", encoding="utf-8") as f:
    f.write("Status: OK\n")
    f.flush()

print(f"Файл успешно создан: {file_path.exists()}")
