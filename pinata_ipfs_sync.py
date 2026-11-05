# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, Jus Cogens, ВДПЧ 1948, TI-ULA

import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

WORKSPACE_DIR = r"H:\ACTOR_DEV_ENV"
MANIFEST_FILE = os.path.join(WORKSPACE_DIR, "INTEGRITY_WITNESS.json")

PINATA_JWT = os.environ.get("PINATA_JWT")
PINATA_API_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"


def pin_to_ipfs():
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] Инициализация IPFS Pinning через Pinata..."
    )

    if not PINATA_JWT:
        print("Ошибка: PINATA_JWT не найден в .env.")
        return

    if not os.path.exists(MANIFEST_FILE):
        print("Ошибка: INTEGRITY_WITNESS.json не найден. IPFS pinning отменен.")
        return

    headers = {"Authorization": f"Bearer {PINATA_JWT}"}

    try:
        with open(MANIFEST_FILE, "rb") as f:
            files = {"file": ("INTEGRITY_WITNESS.json", f, "application/json")}
            response = requests.post(PINATA_API_URL, headers=headers, files=files)

        response.raise_for_status()
        result = response.json()
        ipfs_hash = result.get("IpfsHash")

        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            manifest_data["latest_ipfs_cid"] = ipfs_hash
            manifest_data["latest_ipfs_pin_utc"] = datetime.now(
                timezone.utc
            ).isoformat()

            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=4, ensure_ascii=False)

            print(
                f"[{datetime.now(timezone.utc).isoformat()}] IPFS CID зафиксирован в локальном манифесте."
            )
        except Exception as update_err:
            print(f"Ошибка обновления манифеста: {update_err}")

        print(f"УСПЕШНЫЙ PIN: IPFS CID = {ipfs_hash}")

    except Exception as e:
        print(f"ОШИБКА IPFS PINNING: {str(e)}")


if __name__ == "__main__":
    pin_to_ipfs()
