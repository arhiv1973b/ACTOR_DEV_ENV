import json
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

CREDS_PATH = r'H:\ACTOR_DEV_ENV\keys\credentials.json'

print("[СИСТЕМА] Анализ структуры credentials.json...")
try:
    with open(CREDS_PATH, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
        print(f"[ИНФО] Корневые ключи JSON: {list(data.keys())}")
except Exception as e:
    print(f"[ОШИБКА] Не удалось прочитать JSON: {e}")

print("\n[СИСТЕМА] Тест 1: Инициализация Service Account...")
try:
    service_account.Credentials.from_service_account_file(CREDS_PATH)
    print("[+] Успех: Service Account валиден.")
except Exception as e:
    print(f"[-] Провал: {type(e).__name__} -> {e}")

print("\n[СИСТЕМА] Тест 2: Инициализация OAuth 2.0 (Installed App)...")
try:
    InstalledAppFlow.from_client_secrets_file(CREDS_PATH, ['https://www.googleapis.com/auth/drive.readonly'])
    print("[+] Успех: OAuth 2.0 валиден.")
except Exception as e:
    print(f"[-] Провал: {type(e).__name__} -> {e}")
