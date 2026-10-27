import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_PATH = Path(r"H:\ACTOR_DEV_ENV\credentials.json")
TOKEN_PATH = Path(r"H:\ACTOR_DEV_ENV\token.json")


def get_drive_service():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


if __name__ == "__main__":
    service = get_drive_service()
    about = service.about().get(fields="user").execute()
    print(
        f"✅ Успешная авторизация в Google Drive для пользователя: {about.get('user', {}).get('displayName')}"
    )
