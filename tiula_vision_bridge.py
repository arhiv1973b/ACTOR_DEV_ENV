import os
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDS_PATH = r'H:\ACTOR_DEV_ENV\keys\credentials.json'
TOKEN_PATH = r'H:\ACTOR_DEV_ENV\keys\token.json'
MANIFEST_PATH = r'H:\ACTOR_DEV_ENV\cloud_id_manifest.json'

def authenticate():
    try:
        creds = service_account.Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
        print("[VISION] Авторизация через Service Account успешна.")
        return creds
    except Exception:
        pass

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    print("[VISION] Авторизация через OAuth 2.0 успешна.")
    return creds

def scan_drive():
    print("[VISION] Инициализация Google Drive API...")
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    query = "name = 'A©t0r_Archive' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    folders = service.files().list(q=query, fields="files(id)").execute().get('files', [])

    if not folders:
        print("[ОШИБКА] Корневая папка 'A©t0r_Archive' не найдена в облаке.")
        return

    folder_id = folders[0]['id']
    pdf_files = {}

    def walk_folder(f_id):
        query = f"'{f_id}' in parents and trashed = false"
        files = service.files().list(q=query, fields="files(id, name, mimeType)", pageSize=1000).execute().get('files', [])
        for item in files:
            if item['mimeType'] == 'application/pdf':
                pdf_files[item['name']] = item['id']
            elif item['mimeType'] == 'application/vnd.google-apps.folder':
                walk_folder(item['id'])

    walk_folder(folder_id)
    print(f"[VISION] Найдено {len(pdf_files)} PDF документов в облаке.")

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(pdf_files, f, ensure_ascii=False, indent=2)

    print(f"[VISION] Манифест успешно сохранен: {MANIFEST_PATH}")
    print("\n--- ВЕРИФИКАЦИЯ (Первые 5 записей) ---")
    for count, (k, v) in enumerate(pdf_files.items()):
        if count >= 5: break
        print(f"File: {k} | ID: {v}")
    print("--------------------------------------")

if __name__ == '__main__':
    if not os.path.exists(CREDS_PATH):
        print(f"[ОШИБКА] Файл секретов не найден по пути: {CREDS_PATH}")
    else:
        scan_drive()
