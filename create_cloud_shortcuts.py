import os
import json
import time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
CRED_PATH = Path(r"H:\ACTOR_DEV_ENV\credentials.json")
TOKEN_PATH = Path(r"H:\ACTOR_DEV_ENV\token.json")
POINTERS_DIR = Path(r"H:\ACTOR_DEV_ENV\pointers")

folder_id_cache = {r"F:\Мой диск": "root"}
file_id_cache = {}


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


def get_folder_id(service, folder_path):
    folder_path = str(Path(folder_path).resolve())
    if folder_path in folder_id_cache:
        return folder_id_cache[folder_path]

    parent_dir = str(Path(folder_path).parent)
    folder_name = Path(folder_path).name

    parent_id = get_folder_id(service, parent_dir)
    if not parent_id:
        return None

    safe_name = folder_name.replace("'", "\\'")
    query = f"name = '{safe_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = (
        service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    )
    files = results.get("files", [])

    if files:
        folder_id_cache[folder_path] = files[0]["id"]
        return files[0]["id"]
    return None


def get_file_id(service, file_path):
    file_path = str(Path(file_path).resolve())
    if file_path in file_id_cache:
        return file_id_cache[file_path]

    parent_dir = str(Path(file_path).parent)
    file_name = Path(file_path).name

    parent_id = get_folder_id(service, parent_dir)
    if not parent_id:
        return None

    safe_name = file_name.replace("'", "\\'")
    query = f"name = '{safe_name}' and '{parent_id}' in parents and trashed = false"
    results = (
        service.files().list(q=query, spaces="drive", fields="files(id)").execute()
    )
    files = results.get("files", [])

    if files:
        file_id_cache[file_path] = files[0]["id"]
        return files[0]["id"]
    return None


def create_shortcuts():
    if not POINTERS_DIR.exists():
        print(f"❌ Директория с указателями не найдена: {POINTERS_DIR}")
        return

    pointers = list(POINTERS_DIR.glob("*.pointer.json"))
    if not pointers:
        print("ℹ️ Файлы-указатели не найдены.")
        return

    print(f"🚀 Запуск генерации облачных ярлыков для {len(pointers)} указателей...")
    service = get_drive_service()

    success_count = 0
    error_count = 0

    for i, p in enumerate(pointers, 1):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            master_path = data.get("master_target")
            dup_path = data.get("original_duplicate")

            if data.get("cloud_shortcut_id"):
                print(f"[{i:04d}/{len(pointers)}] ⏭️ Пропуск (ярлык уже есть): {p.name}")
                continue

            master_id = get_file_id(service, master_path)
            if not master_id:
                print(
                    f"[{i:04d}/{len(pointers)}] ⚠️ Мастер не найден в облаке: {Path(master_path).name}"
                )
                error_count += 1
                continue

            dup_parent = str(Path(dup_path).parent)
            parent_id = get_folder_id(service, dup_parent)
            if not parent_id:
                print(
                    f"[{i:04d}/{len(pointers)}] ⚠️ Родительская папка не найдена: {dup_parent}"
                )
                error_count += 1
                continue

            shortcut_metadata = {
                "name": Path(dup_path).name,
                "mimeType": "application/vnd.google-apps.shortcut",
                "parents": [parent_id],
                "shortcutDetails": {"targetId": master_id},
            }

            shortcut = (
                service.files().create(body=shortcut_metadata, fields="id").execute()
            )
            shortcut_id = shortcut.get("id")

            data["cloud_shortcut_id"] = shortcut_id
            data["cloud_shortcut_url"] = (
                f"https://drive.google.com/file/d/{shortcut_id}/view"
            )
            p.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            print(f"[{i:04d}/{len(pointers)}] ✅ Ярлык создан: {Path(dup_path).name}")
            success_count += 1

            time.sleep(0.2)

        except Exception as e:
            print(f"[{i:04d}/{len(pointers)}] ❌ Ошибка {p.name}: {e}")
            error_count += 1

    print("=" * 70)
    print(
        f"🏁 Генерация завершена! Создано ярлыков: {success_count}. Ошибок: {error_count}"
    )


if __name__ == "__main__":
    create_shortcuts()
