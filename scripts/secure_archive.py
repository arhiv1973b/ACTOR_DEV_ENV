#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# [⚖ A©tor Declaration]
Secure Archival Engine for Crypto Manifests
Author: Alexei Macheret (A©tor) | IDNP: 2000001159655
Scope: Jus Cogens, Erga Omnes, UDHR 1948, Hague Convention 1961
"""

import os
import zipfile
from pathlib import Path

try:
    import pyzipper

    HAS_PYZIPPER = True
except ImportError:
    HAS_PYZIPPER = False


def create_secure_archive(source_dir, output_zip, password=None):
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[-] Source directory {source_dir} does not exist.")
        return

    if HAS_PYZIPPER and password:
        # Corrected encryption constant to WZ_AES
        with pyzipper.AESZipFile(
            output_zip,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES,
        ) as zf:
            zf.pwd = password.encode("utf-8")
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path.parent)
                    zf.write(file_path, arcname)
        print(f"[+] Secure AES-256 encrypted archive created: {output_zip}")
    else:
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path.parent)
                    zf.write(file_path, arcname)
        print(f"[+] Standard compressed archive created: {output_zip}")


if __name__ == "__main__":
    pwd = input(
        "Введите пароль для шифрования архива (или оставьте пустым для стандартного архива): "
    ).strip()
    create_secure_archive(
        "05_CRYPTO_MANIFESTS", "05_CRYPTO_MANIFESTS_secure.zip", pwd if pwd else None
    )
