import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive"]
CRED_PATH = Path(r"H:\ACTOR_DEV_ENV\credentials.json")
TOKEN_PATH = Path(r"H:\ACTOR_DEV_ENV\token.json")
MAP_PATH = Path(r"H:\ACTOR_DEV_ENV\duplication_map.json")


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


def find_file_id_by_path(service, local_path):
    # Преобразуем путь F:\Мой диск\папка\файл.pdf в относительный путь Drive
    rel_path = os.path.relpath(local_path, r"F:\Мой диск")
    parts = rel_path.split(os.sep)

    current_parent = "root"
    for i, part in enumerate(parts):
        query = f"name = '{part}' and '{current_parent}' in parents and trashed = false"
        results = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id, name, mimeType)")
            .execute()
        )
        files = results.get("files", [])

        if not files:
            return None

        # Если это последний элемент (сам файл)
        if i == len(parts) - 1:
            return files[0]["id"]
        else:
            # Ищем среди папок
            folder = next(
                (
                    f
                    for f in files
                    if f["mimeType"] == "application/vnd.google-apps.folder"
                ),
                None,
            )
            if folder:
                current_parent = folder["id"]
            else:
                return None
    return None


def main():
    if not MAP_PATH.exists():
        print(f"❌ Карта дубликатов не найдена: {MAP_PATH}")
        return

    service = get_drive_service()
    print("✅ Подключение к Google Drive API успешно установлено.")

    with open(MAP_PATH, "r", encoding="utf-8") as f:
        container = json.load(f)

    for group in container.get("duplication_map", []):
        if group.get("status") != "PENDING_POINTER_REPLACEMENT":
            continue

        master_path = group["master_file"]
        master_id = find_file_id_by_path(service, master_path)

        if not master_id:
            print(f"⚠️ Не найден master-файл в облаке: {master_path}")
            continue

        print(f"📌 Обработка группы (Master ID: {master_id})")

        resolved_duplicates = []
        for dup_path in group["duplicates"]:
            dup_id = find_file_id_by_path(service, dup_path)
            if not dup_id:
                print(f"  ⚠️ Дубликат не найден в облаке: {dup_path}")
                continue

            # Получаем родительскую папку дубликата
            file_meta = service.files().get(fileId=dup_id, fields="parents").execute()
            parents = file_meta.get("parents", [])
            parent_id = parents[0] if parents else "root"

            # Шаг 1: Создаем ярлык (Shortcut) на master-файл
            shortcut_metadata = {
                "name": os.path.basename(dup_path),
                "mimeType": "application/vnd.google-apps.shortcut",
                "parents": [parent_id],
                "shortcutDetails": {"targetId": master_id},
            }
            shortcut = (
                service.files().create(body=shortcut_metadata, fields="id").execute()
            )
            shortcut_id = shortcut.get("id")
            shortcut_url = f"https://drive.google.com/file/d/{shortcut_id}/view"
            print(
                f"  🔗 Создан ярлык для: {os.path.basename(dup_path)} (ID: {shortcut_id})"
            )

            # Шаг 2: Отправляем физический дубликат в корзину (безопасно)
            service.files().update(fileId=dup_id, body={"trashed": True}).execute()
            print(f"  🗑️ Дубликат перемещен в корзину облака: {dup_path}")

            resolved_duplicates.append(
                {
                    "path": dup_path,
                    "file_id": dup_id,
                    "shortcut_id": shortcut_id,
                    "shortcut_url": shortcut_url,
                }
            )

        group["status"] = "POINTER_RESOLVED"
        group["resolved_details"] = resolved_duplicates

    # Сохраняем обновленную карту
    MAP_PATH.write_text(
        json.dumps(container, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"✅ Обработка завершена. Обновленная карта сохранена в {MAP_PATH}")


if __name__ == "__main__":
    main()
