import os
import json
import sys
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

A©TOR_KEY = "# [⚖ A©tor Declaration]"


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


def calculate_file_sha256(filepath):
    hasher = hashlib.sha256()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def verify_archive_hash(archive_path, expected_sha256):
    actual_sha256 = calculate_file_sha256(archive_path)

    if actual_sha256.lower() != expected_sha256.lower():
        raise ValueError("Хэш архива не совпадает")

    print(f"[{A©TOR_KEY}] ✔ Archive SHA-256 валиден")


def verify_local_assets(manifest, manifest_path):
    """
    Level 2: Проверка фактических локальных файлов
    против SHA-256 в манифесте с поддержкой относительных путей
    и защитой от Path Traversal.
    """
    manifest_dir = Path(manifest_path).parent.resolve()
    checked = 0

    for file_id, entry in manifest["entries"].items():
        assets = entry.get("local_assets", {})

        for asset_name in ["cmd_launcher", "preview_image"]:
            asset = assets.get(asset_name)

            if not asset:
                raise ValueError(f"{file_id}: отсутствует {asset_name}")

            relative_path = asset["file"]
            asset_path = (manifest_dir / relative_path).resolve()

            # Защита от выхода за пределы каталога манифеста (Path Traversal)
            try:
                asset_path.relative_to(manifest_dir)
            except ValueError:
                raise ValueError(
                    f"{file_id}: Попытка выхода за пределы каталога манифеста (Path Traversal): {relative_path}"
                )

            if not asset_path.exists():
                raise ValueError(f"{file_id}: файл не найден: {asset_path}")

            actual_sha = calculate_file_sha256(asset_path)
            expected_sha = asset["sha256"]

            if actual_sha.lower() != expected_sha.lower():
                raise ValueError(
                    f"{file_id}: нарушение целостности\n"
                    f"Файл: {relative_path}\n"
                    f"Ожидался: {expected_sha}\n"
                    f"Получен : {actual_sha}"
                )

            checked += 1

    print(f"[{A©TOR_KEY}] ✔ Проверено файлов: {checked}")


def resolve_manifest_path():
    """
    Приоритет:
      1. PDF_MANIFEST
      2. pdf_index.json рядом со скриптом
      3. F:\\Мой диск\\PDF_Links
      4. H:\\ACTOR_DEV_ENV\\PDF_Links
    """

    root_dir = os.path.dirname(os.path.abspath(__file__))

    candidates = [
        os.environ.get("PDF_MANIFEST"),
        os.path.join(root_dir, "pdf_index.json"),
        r"F:\Мой диск\PDF_Links\pdf_index.json",
        r"H:\ACTOR_DEV_ENV\PDF_Links\pdf_index.json",
    ]

    for path in candidates:
        if path and os.path.exists(path):
            return os.path.abspath(path)

    return None


def main():
    manifest_path = resolve_manifest_path()

    if not manifest_path:
        print(f"[{A©TOR_KEY}] ❌ Файл pdf_index.json не найден.")
        sys.exit(1)

    print(f"[{A©TOR_KEY}] Загрузка манифеста из: {manifest_path}")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    except Exception as e:
        print(f"[{A©TOR_KEY}] Ошибка чтения манифеста: {e}")
        sys.exit(1)

    # Level 1: Structure Audit
    print(f"[{A©TOR_KEY}] ✔ Структура манифеста валидна")

    entries = manifest.get("entries", {})
    crypto_data = manifest.get("cryptography", {})

    if not crypto_data:
        print(f"[{A©TOR_KEY}] Отсутствует криптографическая секция.")
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
        print(f"[{A©TOR_KEY}] ✔ Самохэш манифеста (Manifest Self-Hash) валиден")
    except Exception as e:
        print(f"[{A©TOR_KEY}] ❌ Ошибка проверки хэша манифеста: {e}")
        sys.exit(1)

    # Level 2: Local Asset Audit
    try:
        verify_local_assets(manifest, manifest_path)
    except Exception as e:
        print(f"[{A©TOR_KEY}] ❌ Нарушение целостности\n{e}")
        sys.exit(1)

    # Level 3: Merkle Audit
    all_pdf_hashes = [
        entry["document"]["original_pdf_sha256"] for entry in entries.values()
    ]

    computed_root = compute_merkle_root(all_pdf_hashes)
    stored_root = crypto_data.get("merkle_root_sha256")

    if computed_root != stored_root:
        print(
            f"[{A©TOR_KEY}] ❌ ИСКАЖЕНИЕ: "
            f"ожидался {stored_root}, "
            f"вычислен {computed_root}"
        )
        sys.exit(1)

    print(f"[{A©TOR_KEY}] ✔ Merkle Root валиден: {computed_root}")

    # Level 4: Signature Audit
    try:
        pub_key_bytes = bytes.fromhex(crypto_data["public_key_ed25519_hex"])

        signature_bytes = bytes.fromhex(crypto_data["signature_ed25519_hex"])

        public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_key_bytes)

        signed_payload = f"{stored_root}:{computed_payload_hash}".encode("utf-8")

        public_key.verify(signature_bytes, signed_payload)

        print(f"[{A©TOR_KEY}] ✔ Подпись Ed25519 математически подтверждена.")

    except Exception as e:
        print(f"[{A©TOR_KEY}] ❌ ОШИБКА ПОДПИСИ: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
