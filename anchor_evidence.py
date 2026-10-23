#!/usr/bin/env python3
import hashlib
import json
import os
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# Целевые файлы для крипто-фиксации (content-addressing)
FILES_TO_ANCHOR = [
    "FORENSIC_FINCOM_ANALYSIS.md",
    "JUS_COGENS_ERGA_OMNES_MASTER_SYNTHESIS.md",
    "IDENTITY_DISTORTION_GRAPH.md",
    "actor_jus_cogens_engine.json",
    "🏛️ EVIDENCE/New_Submissions/[⚖ A©tor Declaration] .pdf",
    "🏛️ EVIDENCE/New_Submissions/Навстречу к Справедливому Возврату - последнее предупреждение в досудебном порядке.pdf",
]


def generate_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    print("=== TI-ULA: Cryptographic Anchoring (Ed25519/SHA-256) ===")

    # Инициализация или загрузка ключа A©tor
    key_path = "actor_ed25519_key.pem"
    if not os.path.exists(key_path):
        print("[+] Генерируем новый приватный ключ Ed25519...")
        private_key = ed25519.Ed25519PrivateKey.generate()
        with open(key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
    else:
        print("[+] Загрузка существующего ключа Ed25519...")
        with open(key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

    manifest = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "case_id": "CASE-MACHERET-1997-2026",
        "legal_basis": "Jus Cogens / Erga Omnes",
        "anchors": [],
    }

    for filepath in FILES_TO_ANCHOR:
        file_hash = generate_sha256(filepath)
        if file_hash:
            # Подпись хеша ключом Ed25519
            signature = private_key.sign(file_hash.encode("utf-8"))
            manifest["anchors"].append(
                {
                    "file": filepath,
                    "sha256": file_hash,
                    "ed25519_signature": signature.hex(),
                }
            )
            print(f"Locked: {filepath}\n -> SHA-256: {file_hash}")
        else:
            print(f"[!] Файл не найден: {filepath}")

    # Сохранение криптографического манифеста
    with open("ti_ula_crypto_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print("\n[✓] Манифест ti_ula_crypto_manifest.json успешно сгенерирован.")


if __name__ == "__main__":
    main()
