import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CRED_PATH = Path(r"H:\ACTOR_DEV_ENV\credentials.json")
TOKEN_PATH = Path(r"H:\ACTOR_DEV_ENV\token.json")


def get_drive_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CRED_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def check_quota():
    try:
        service = get_drive_service()
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get("storageQuota", {})

        limit_gb = int(quota.get("limit", 0)) / (1024**3)
        usage_gb = int(quota.get("usage", 0)) / (1024**3)
        trash_gb = int(quota.get("usageInDriveTrash", 0)) / (1024**3)

        print("☁️ Статус хранилища Google Drive API:")
        print(f"  • Всего доступно: {limit_gb:.2f} ГБ")
        print(f"  • Занято сейчас:  {usage_gb:.2f} ГБ")
        print(
            f"  • Застряло в корзине: {trash_gb:.2f} ГБ (нужно очистить для освобождения места)"
        )
    except Exception as e:
        print(f"❌ Ошибка проверки квоты: {e}")


if __name__ == "__main__":
    check_quota()
