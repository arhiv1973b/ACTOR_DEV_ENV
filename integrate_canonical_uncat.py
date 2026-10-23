#!/usr/bin/env python3
"""
Canonical UNCAT 1984 Integration
Копирует 'конвенция 1884 пытки6..json' в UNCAT_1984_canonical.json и связывает с Ядром Причинности.
"""

import os
import shutil
import json
import yaml


def integrate_canonical():
    src = r"C:\Users\arhiv\Downloads\Downolde\конвенция 1884 пытки6..json"
    base_dir = "H:\\ACTOR_DEV_ENV"
    dest = os.path.join(base_dir, "UNCAT_1984_canonical.json")

    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"[*] Канонический файл UNCAT успешно скопирован: {dest}")
    else:
        print("[-] Исходный файл не найден.")
        return

    with open(dest, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to YAML as well
    yaml_dest = os.path.join(base_dir, "UNCAT_1984_canonical.yaml")
    with open(yaml_dest, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"[*] Сгенерирован канонический YAML: {yaml_dest}")


if __name__ == "__main__":
    integrate_canonical()
