import os
import sys
import json
import requests

# Конфигурация
ACCESS_TOKEN = os.environ.get("ZENODO_TOKEN", "УКАЖИТЕ_ВАШ_ТОКЕН_ЗДЕСЬ")
BASE_URL = "https://zenodo.org/api/deposit/depositions"
METADATA_FILE = "zenodo_deposit_metadata.json"
REPORT_FILE = "ERGA_OMNES_AUDIT_REPORT_2026.txt"

print("=== ИНИЦИАЦИЯ СОЕДИНЕНИЯ С ZENODO API ===")
if ACCESS_TOKEN == "УКАЖИТЕ_ВАШ_ТОКЕН_ЗДЕСЬ":
    print("[-] ОШИБКА: Необходим персональный API-токен Zenodo (ZENODO_TOKEN).")
    sys.exit(1)

# 1. Создание пустого депозита и резервирование DOI
print("[+] Регистрация нового слота депозита...")
r = requests.post(
    BASE_URL,
    params={"access_token": ACCESS_TOKEN},
    json={},
    headers={"Content-Type": "application/json"},
)
if r.status_code not in [200, 201]:
    print(f"[-] Ошибка API: {r.text}")
    sys.exit(1)

dep_data = r.json()
dep_id = dep_data["id"]
bucket_url = dep_data["links"]["bucket"]
reserved_doi = dep_data["metadata"]["prereserve_doi"]["doi"]
print(f"[+] Слот создан. Зарезервированный DOI: {reserved_doi}")

# 2. Загрузка метаданных Erga Omnes
print("[+] Привязка метаданных из zenodo_deposit_metadata.json...")
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    metadata = json.load(f)
r = requests.put(
    f"{BASE_URL}/{dep_id}",
    params={"access_token": ACCESS_TOKEN},
    json={"metadata": metadata},
)

# 3. Загрузка криптографического отчета
print(f"[+] Выгрузка артефакта: {REPORT_FILE}...")
with open(REPORT_FILE, "rb") as f:
    r = requests.put(
        f"{bucket_url}/{REPORT_FILE}", params={"access_token": ACCESS_TOKEN}, data=f
    )

print(
    "================================================================================"
)
print("✅ DOI GENERATION STAGED SUCCESSFULLY")
print(f"🔗 Pre-reserved DOI: https://doi.org/{reserved_doi}")
print(
    f"⚠️ Для финальной публикации (Publish) перейдите в панель Zenodo и подтвердите депозит."
)
print(
    "================================================================================"
)
