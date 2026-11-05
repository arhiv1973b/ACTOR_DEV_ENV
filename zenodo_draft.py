# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, Jus Cogens, ВДПЧ 1948, TI-ULA

import os
import json
import glob
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

WORKSPACE_DIR = r"H:\ACTOR_DEV_ENV"
SECURE_LOGS_DIR = os.path.join(WORKSPACE_DIR, "secure_logs")
MANIFEST_FILE = os.path.join(WORKSPACE_DIR, "INTEGRITY_WITNESS.json")

ZENODO_ACCESS_TOKEN = os.environ.get("ZENODO_TOKEN")
ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"


def create_zenodo_draft():
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Инициализация Zenodo Draft DOI..."
    )

    if not ZENODO_ACCESS_TOKEN:
        print("Ошибка: ZENODO_TOKEN не найден в .env.")
        return

    if not os.path.exists(MANIFEST_FILE):
        print("Ошибка: INTEGRITY_WITNESS.json не найден.")
        return

    sig_files = glob.glob(os.path.join(SECURE_LOGS_DIR, "*.sig"))
    latest_sig_file = max(sig_files, key=os.path.getmtime) if sig_files else None

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        ipfs_cid = manifest_data.get("latest_ipfs_cid", "N/A")
        merkle_root = manifest_data.get("secure_logs_merkle_root", "N/A")
    except Exception as e:
        print(f"Ошибка парсинга манифеста: {e}")
        return

    headers = {"Content-Type": "application/json"}
    params = {"access_token": ZENODO_ACCESS_TOKEN}

    try:
        r = requests.post(ZENODO_API_URL, params=params, json={}, headers=headers)
        r.raise_for_status()
        deposition = r.json()

        deposition_id = deposition["id"]
        draft_doi = deposition["metadata"]["prereserve_doi"]["doi"]
        bucket_url = deposition["links"]["bucket"]

        sig_info = (
            f"<br>Ed25519 Signature: <strong>{os.path.basename(latest_sig_file)}</strong>"
            if latest_sig_file
            else ""
        )

        metadata = {
            "metadata": {
                "title": f"TI-ULA Evidence Vault Snapshot [{datetime.now(timezone.utc).strftime('%Y-%m-%d')}]",
                "upload_type": "dataset",
                "description": f"Google Drive & OneDrive Evidence Vault.<br>IPFS CID: <strong>{ipfs_cid}</strong><br>Merkle Root: {merkle_root}{sig_info}",
                "creators": [
                    {"name": "Macheret, Alexei (A©t0r)", "affiliation": "TI-ULA"}
                ],
                "keywords": [
                    "Erga Omnes",
                    "Jus Cogens",
                    "TI-ULA",
                    "Google Drive",
                    "Ed25519",
                    "Evidence Vault",
                ],
            }
        }

        requests.put(
            f"{ZENODO_API_URL}/{deposition_id}",
            params=params,
            json=metadata,
            headers=headers,
        ).raise_for_status()

        files_to_upload = [MANIFEST_FILE]
        if latest_sig_file:
            files_to_upload.append(latest_sig_file)

        for file_path in files_to_upload:
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as fp:
                requests.put(
                    f"{bucket_url}/{file_name}", data=fp, params=params
                ).raise_for_status()

        manifest_data["latest_zenodo_draft_doi"] = draft_doi
        manifest_data["latest_zenodo_deposition_id"] = deposition_id
        manifest_data["latest_zenodo_sync_utc"] = datetime.now(timezone.utc).isoformat()

        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=4, ensure_ascii=False)

        print(f"ЗАРЕГИСТРИРОВАННЫЙ DOI: {draft_doi}")

    except Exception as e:
        print(f"ОШИБКА ZENODO API: {str(e)}")


if __name__ == "__main__":
    create_zenodo_draft()
