from __future__ import annotations
import os
import hashlib
import json
from pathlib import Path
import logging
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().lower()


def verify_integrity(downloads_dir: str | Path, registry_json_path: str | Path) -> bool:
    downloads_path = Path(downloads_dir)
    registry_path = Path(registry_json_path)

    if not registry_path.exists():
        LOGGER.error(f"Реестр не найден: {registry_path}")
        return False

    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        registry = data.get("entries", data)

    total = len(registry)
    passed = 0
    failed = 0
    missing = 0

    LOGGER.info(
        f"[*] Начало проверки целостности {total} записей в каталоге: {downloads_path}"
    )

    for entry in registry:
        expected_hash = entry.get("sha256")
        local_file_rel = entry.get("local_file")
        
        # Resolve path relative to repository root / downloads_dir fallback
        file_path = Path(local_file_rel) if local_file_rel else downloads_path / (entry.get("apostille") + ".pdf")
        if not file_path.is_absolute() and not file_path.exists():
            # Try combining downloads_dir with filename
            file_path = downloads_path / Path(local_file_rel).name if local_file_rel else downloads_path / f"apostille_{entry.get('apostille')}.pdf"

        if not expected_hash:
            LOGGER.warning(
                f"[-] Запись без SHA-256 хэша для апостиля: {entry.get('apostille')}"
            )
            failed += 1
            continue

        if not file_path.exists():
            LOGGER.error(
                f"[X] Файл отсутствует: {file_path.name} (Апостиль: {entry.get('apostille')})"
            )
            missing += 1
            continue

        actual_hash = calculate_sha256(file_path)
        if actual_hash == expected_hash.lower():
            passed += 1
        else:
            LOGGER.error(
                f"[!] Несовпадение хэша для {file_path.name}! Ожидался: {expected_hash}, получен: {actual_hash}"
            )
            failed += 1

    LOGGER.info("=" * 50)
    LOGGER.info(f"Результаты проверки целостности:")
    LOGGER.info(f"  Всего записей: {total}")
    LOGGER.info(f"  Успешно проверено (Passed): {passed}")
    LOGGER.info(f"  Отсутствует (Missing): {missing}")
    LOGGER.info(f"  Ошибка хэша (Failed): {failed}")
    LOGGER.info("=" * 50)

    return failed == 0 and missing == 0


if __name__ == "__main__":
    downloads_dir = os.environ.get("DOWNLOADS_DIR", "exports/downloads")
    registry_path = os.environ.get("REGISTRY_JSON", "INTEGRITY_WITNESS.json")

    success = verify_integrity(downloads_dir, registry_path)
    if not success:
        sys.exit(1)
    else:
        print("[OK] Все файлы прошли проверку целостности успешно.")
