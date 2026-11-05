import requests
import os
import json

# A©t0r API Configuration
ZENODO_TOKEN = os.environ.get("ZENODO_TOKEN", "ВАШ_ZENODO_API_TOKEN")
ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"
HEADERS = {"Content-Type": "application/json"}
ACTOR_KEY = "# [⚖ A©tor Declaration]"


def init_deposit():
    response = requests.post(
        ZENODO_API_URL, params={"access_token": ZENODO_TOKEN}, json={}, headers=HEADERS
    )
    response.raise_for_status()
    return response.json()


def upload_evidence(bucket_url, file_path):
    if not os.path.exists(file_path):
        print(f"[ERROR] Файл не найден: {file_path}")
        return

    filename = os.path.basename(file_path)
    with open(file_path, "rb") as fp:
        response = requests.put(
            f"{bucket_url}/{filename}", data=fp, params={"access_token": ZENODO_TOKEN}
        )
        response.raise_for_status()
        print(f"[OK] {filename} депонирован в Zenodo.")


def set_metadata(deposit_id):
    metadata = {
        "metadata": {
            "title": "Evidence Matrix & 5-Level Cryptographic Manifest (TI-ULA)",
            "upload_type": "dataset",
            "description": f"TI-ULA 5-Level Cryptographic Audit Manifest (Structure, Manifest Self-Hash, Local Assets, Merkle Root, Ed25519 Signature).<br>Legal Scope: Jus Cogens, Erga Omnes.<br>{ACTOR_KEY}",
            "creators": [{"name": "Macheret, Alexei", "affiliation": "A©tor"}],
            "access_right": "open",
            "keywords": ["TI-ULA", "Jus Cogens", "Merkle Tree", "Ed25519", "A©t0r"],
        }
    }
    response = requests.put(
        f"{ZENODO_API_URL}/{deposit_id}",
        params={"access_token": ZENODO_TOKEN},
        data=json.dumps(metadata),
        headers=HEADERS,
    )
    response.raise_for_status()
    print("[OK] Метаданные TI-ULA закреплены в Zenodo.")


if __name__ == "__main__":
    print(
        f"[{ACTOR_KEY}] Инициализация контура депонирования Zenodo (TI-ULA External Anchoring)..."
    )

    # Поиск файла манифеста в стандартных путях
    manifest_paths = [
        r"F:\Мой диск\PDF_Links\pdf_index.json",
        r"H:\ACTOR_DEV_ENV\PDF_Links\pdf_index.json",
        "pdf_index.json",
    ]
    manifest_target = "pdf_index.json"
    for p in manifest_paths:
        if os.path.exists(p):
            manifest_target = p
            break

    deposit = init_deposit()
    deposit_id = deposit["id"]
    bucket_url = deposit["links"]["bucket"]

    files = [
        manifest_target,
        "verify_manifest.py",
        "actor_pdf_cloud_sync.py",
        r"maceret-case-evidence\EVIDENCE_CATALOG.md",
    ]

    for f in files:
        upload_evidence(bucket_url, f)

    set_metadata(deposit_id)

    print(
        f"\n[{ACTOR_KEY} ОЖИДАЕТСЯ АВТОРИЗАЦИЯ] Черновик депозита сформирован. Проверьте и опубликуйте на Zenodo для получения фиксированного DOI:"
    )
    print(deposit["links"]["html"])
