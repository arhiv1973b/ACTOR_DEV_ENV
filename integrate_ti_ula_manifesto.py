#!/usr/bin/env python3
"""
TI-ULA Manifesto Integrator
Копирует TI_ULA_MANIFESTO.html в корневой каталог и директорию docs/,
интегрирует его в систему документации и связывает с Ядром Причинности.
"""

import os
import shutil


def integrate_manifesto():
    src = r"C:\Users\arhiv\Downloads\Downolde\TI_ULA_MANIFESTO.html"
    base_dir = "H:\\ACTOR_DEV_ENV"

    dest_root = os.path.join(base_dir, "TI_ULA_MANIFESTO.html")
    docs_dir = os.path.join(base_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    dest_docs = os.path.join(docs_dir, "TI_ULA_MANIFESTO.html")

    if os.path.exists(src):
        shutil.copy2(src, dest_root)
        shutil.copy2(src, dest_docs)
        print(
            f"[*] TI-ULA Manifesto успешно интегрирован в корневой каталог и docs/: {dest_root}"
        )
    else:
        print("[-] Исходный файл манифеста не найден.")


if __name__ == "__main__":
    integrate_manifesto()
