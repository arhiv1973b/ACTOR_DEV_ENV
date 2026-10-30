import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
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


def manage_trash():
    print("🔄 Подключение к Google Drive API...")
    try:
        service = get_drive_service()
        about = service.about().get(fields="storageQuota").execute()
        quota = about.get("storageQuota", {})

        limit_gb = int(quota.get("limit", 0)) / (1024**3) if quota.get("limit") else 0
        usage_gb = int(quota.get("usage", 0)) / (1024**3)
        trash_gb = int(quota.get("usageInDriveTrash", 0)) / (1024**3)

        print("\n☁️ ТЕКУЩИЙ СТАТУС ХРАНИЛИЩА GOOGLE DRIVE:")
        if limit_gb > 0:
            print(f"  • Всего доступно: {limit_gb:.2f} ГБ")
        print(f"  • Занято сейчас:  {usage_gb:.2f} ГБ")
        print(f"  • Застряло в корзине: {trash_gb:.2f} ГБ")

        if trash_gb > 0.1:  # Если в корзине больше 100 МБ
            print("\n⚠️ В корзине найдены данные. Выполняю запрос на очистку...")
            service.files().emptyTrash().execute()
            print("✅ Команда на очистку корзины успешно отправлена!")
            print(
                "⏳ Серверам Google может потребоваться несколько минут для пересчета квоты."
            )
        else:
            print(
                "\nℹ️ Корзина пуста (или занимает незначительный объем). Очистка не требуется."
            )

    except Exception as e:
        print(f"❌ Ошибка при обращении к API: {e}")


if __name__ == "__main__":
    manage_trash()
