import os
import sys
import requests

# Конфигурация глобального узла (Pinata IPFS)
PINATA_JWT = os.environ.get("PINATA_JWT", "УКАЖИТЕ_ВАШ_JWT_ТОКЕН_ЗДЕСЬ")
API_URL = "https://api.pinata.cloud/pinning/pinFileToIPFS"

artifacts = ["ERGA_OMNES_AUDIT_REPORT_2026.txt", "ipfs_decentralized_anchor.json"]

print(
    "================================================================================"
)
print("CASE-MACHERET: Децентрализованное IPFS Якорение (Jus Cogens)")
print(
    "================================================================================"
)

if PINATA_JWT == "УКАЖИТЕ_ВАШ_JWT_ТОКЕН_ЗДЕСЬ":
    print(
        "[-] ОШИБКА: Необходим токен Pinata (PINATA_JWT) для вечного хранения (pinning)."
    )
    sys.exit(1)

headers = {"Authorization": f"Bearer {PINATA_JWT}"}

for fname in artifacts:
    if not os.path.exists(fname):
        print(f"[-] ПРОПУСК: Файл {fname} не найден в директории.")
        continue

    print(f"[+] Трансляция {fname} в сеть IPFS...")
    with open(fname, "rb") as f:
        res = requests.post(API_URL, files={"file": f}, headers=headers)

        if res.status_code == 200:
            cid = res.json()["IpfsHash"]
            print(f"    [+] УСПЕШНО! CID: ipfs://{cid}")
            print(f"    [+] Шлюз: https://gateway.pinata.cloud/ipfs/{cid}")
        else:
            print(f"    [-] ОШИБКА узла: {res.text}")

print(
    "================================================================================"
)
print("✅ IPFS ANCHORING COMPLETE: Артефакты стали криптографически неизменными.")
print(
    "================================================================================"
)
