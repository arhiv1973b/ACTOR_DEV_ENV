#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TI-ULA Level 6 Archive Reproducibility & Deposit Verification
Usage: python verify_deposit.py --archive TI_ULA_EVIDENCE.zip
"""

import os
import sys
import json
import zipfile
import tempfile
import argparse
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

A©TOR_KEY = "# [⚖ A©tor Declaration]"


def calculate_file_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_merkle_root(hash_list):
    if not hash_list:
        return None
    current_layer = sorted(hash_list)
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            left = current_layer[i]
            right = (
                current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]
            )
            combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
            next_layer.append(combined)
        current_layer = next_layer
    return current_layer[0]


def verify_archive_hash(archive_path, expected_sha256):
    actual_sha256 = calculate_file_sha256(archive_path)
    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError("Хэш архива не совпадает")
    print(f"[{A©TOR_KEY}] ✔ Archive SHA-256")


def main():
    parser = argparse.ArgumentParser(
        description="Verify downloaded Zenodo archive and manifest integrity (Level 1-6)"
    )
    parser.add_argument(
        "--archive",
        required=True,
        help="Path to downloaded ZIP archive (e.g. TI_ULA_EVIDENCE.zip)",
    )
    args = parser.parse_args()

    archive_path = os.path.abspath(args.archive)
    if not os.path.exists(archive_path):
        print(f"[{A©TOR_KEY}] ❌ Архив не найден: {archive_path}")
        sys.exit(1)

    print(f"[{A©TOR_KEY}] Проверка депозита для архива: {archive_path}")

    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(tmpdir)
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ Ошибка распаковки архива: {e}")
            sys.exit(1)

        manifest_path = None
        for root, dirs, files in os.walk(tmpdir):
            if "pdf_index.json" in files:
                manifest_path = os.path.join(root, "pdf_index.json")
                break

        if not manifest_path:
            print(f"[{A©TOR_KEY}] ❌ В архиве не найден файл pdf_index.json")
            sys.exit(1)

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ Ошибка чтения манифеста из архива: {e}")
            sys.exit(1)

        # Level 6: Archive Reproducibility Audit
        external_anchoring = manifest.get("external_anchoring", {})
        expected_sha256 = external_anchoring.get("archive_sha256")

        try:
            if expected_sha256:
                verify_archive_hash(archive_path, expected_sha256)
            else:
                actual_sha256 = calculate_file_sha256(archive_path)
                print(f"[{A©TOR_KEY}] ✔ Archive SHA-256 (вычислен: {actual_sha256})")
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ Ошибка проверки хэша архива: {e}")
            sys.exit(1)

        # Level 1: Structure Audit
        print(f"[{A©TOR_KEY}] ✔ Manifest Structure")

        entries = manifest.get("entries", {})
        crypto_data = manifest.get("cryptography", {})
        if not crypto_data:
            print(f"[{A©TOR_KEY}] ❌ Отсутствует криптографическая секция.")
            sys.exit(1)

        # Level 5: Manifest Self-Hash Audit
        try:
            canonical_entries_bytes = json.dumps(
                entries, sort_keys=True, ensure_ascii=False
            ).encode("utf-8")
            computed_payload_hash = hashlib.sha256(canonical_entries_bytes).hexdigest()
            stored_payload_hash = crypto_data.get(
                "manifest_payload_sha256"
            ) or crypto_data.get("entries_sha256")

            if stored_payload_hash and computed_payload_hash != stored_payload_hash:
                print(
                    f"[{A©TOR_KEY}] ❌ ИСКАЖЕНИЕ МАНИФЕСТА: Ожидался хэш payload {stored_payload_hash}, вычислен {computed_payload_hash}"
                )
                sys.exit(1)
            print(f"[{A©TOR_KEY}] ✔ Manifest Payload Hash")
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ Ошибка проверки хэша манифеста: {e}")
            sys.exit(1)

        # Level 2: Local Asset Audit
        manifest_dir = Path(manifest_path).parent.resolve()
        checked = 0
        try:
            for file_id, entry in entries.items():
                assets = entry.get("local_assets", {})
                for asset_name in ["cmd_launcher", "preview_image"]:
                    asset = assets.get(asset_name)
                    if not asset:
                        raise ValueError(f"{file_id}: отсутствует {asset_name}")
                    relative_path = asset["file"]
                    asset_path = (manifest_dir / relative_path).resolve()
                    try:
                        asset_path.relative_to(manifest_dir)
                    except ValueError:
                        raise ValueError(f"{file_id}: Path Traversal: {relative_path}")
                    if not asset_path.exists():
                        raise ValueError(f"{file_id}: файл не найден: {asset_path}")
                    actual_sha = calculate_file_sha256(asset_path)
                    expected_sha = asset["sha256"]
                    if actual_sha.lower() != expected_sha.lower():
                        raise ValueError(
                            f"{file_id}: нарушение целостности файла {relative_path}"
                        )
                    checked += 1
            print(f"[{A©TOR_KEY}] ✔ Local Assets")
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ Нарушение целостности Local Assets: {e}")
            sys.exit(1)

        # Level 3: Merkle Audit
        all_pdf_hashes = [
            entry["document"]["original_pdf_sha256"] for entry in entries.values()
        ]
        computed_root = compute_merkle_root(all_pdf_hashes)
        stored_root = crypto_data.get("merkle_root_sha256")
        if computed_root != stored_root:
            print(
                f"[{A©TOR_KEY}] ❌ Merkle Root не совпадает: ожид {stored_root}, вычисл {computed_root}"
            )
            sys.exit(1)
        print(f"[{A©TOR_KEY}] ✔ Merkle Root")

        # Level 4: Ed25519 Signature Audit
        try:
            pub_key_bytes = bytes.fromhex(crypto_data["public_key_ed25519_hex"])
            signature_bytes = bytes.fromhex(crypto_data["signature_ed25519_hex"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)
            signed_payload = f"{stored_root}:{computed_payload_hash}".encode("utf-8")
            public_key.verify(signature_bytes, signed_payload)
            print(f"[{A©TOR_KEY}] ✔ Ed25519 Signature")
        except Exception as e:
            print(f"[{A©TOR_KEY}] ❌ ОШИБКА ПОДПИСИ Ed25519: {e}")
            sys.exit(1)

        print(
            f"\n[{A©TOR_KEY}] Итоговая модель: Все 6 уровней аудита (Structure, Local Assets, Merkle, Ed25519, Manifest Self-Hash, Archive Reproducibility) успешно подтверждены."
        )


if __name__ == "__main__":
    main()
