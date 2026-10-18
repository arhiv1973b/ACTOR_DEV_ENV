import os
import zipfile
import hashlib
import datetime

OUTPUT_ZIP = r"H:\ACTOR_DEV_ENV\MASTER_DOSSIER_PACKAGE_2026.zip"
DOSSIER_DIR = r"H:\ACTOR_DEV_ENV\MASTER_DOSSIER"

FILES_TO_INCLUDE = [
    r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.json",
    r"H:\ACTOR_DEV_ENV\VECTOR_ENTITY_EXTRACTION_REPORT.md",
    r"H:\ACTOR_DEV_ENV\dag_manifest.json",
    r"H:\ACTOR_DEV_ENV\entity_graph_network.html",
    r"H:\ACTOR_DEV_ENV\VIBER_DOWNLOADS_FORENSIC_AUDIT.md",
]


def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def main():
    print(
        "[*] Сборка финального юридического пакета MASTER_DOSSIER_PACKAGE_2026.zip..."
    )

    manifest_entries = []

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Добавляем файлы из MASTER_DOSSIER
        if os.path.exists(DOSSIER_DIR):
            for root, dirs, files in os.walk(DOSSIER_DIR):
                for file in files:
                    fp = os.path.join(root, file)
                    arcname = os.path.relpath(fp, r"H:\ACTOR_DEV_ENV")
                    zipf.write(fp, arcname)
                    file_hash = calculate_sha256(fp)
                    manifest_entries.append({"file": arcname, "sha256": file_hash})
                    print(f" [+] Добавлено в архив: {arcname}")

        # Добавляем корневые отчеты
        for fp in FILES_TO_INCLUDE:
            if os.path.exists(fp):
                arcname = os.path.basename(fp)
                zipf.write(fp, arcname)
                file_hash = calculate_sha256(fp)
                manifest_entries.append({"file": arcname, "sha256": file_hash})
                print(f" [+] Добавлено в архив: {arcname}")

        # Создаем манифест архива внутри или рядом
        manifest_data = {
            "package_name": "MASTER_DOSSIER_PACKAGE_2026.zip",
            "created_at": datetime.datetime.now().isoformat(),
            "target_idnp": "2000001159655",
            "key_anchor": "Aviz № 269",
            "files": manifest_entries,
        }

        manifest_json_str = json.dumps(manifest_data, ensure_ascii=False, indent=4)
        zipf.writestr("PACKAGE_MANIFEST_SHA256.json", manifest_json_str)
        print(" [+] Добавлено в архив: PACKAGE_MANIFEST_SHA256.json")

    print(f"\n[✔] Пакет успешно собран: {OUTPUT_ZIP}")


if __name__ == "__main__":
    import json

    main()
