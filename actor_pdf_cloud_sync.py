import os
import io
import json
import hashlib
import re
import fitz  # PyMuPDF
from PIL import Image
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

A©TOR_KEY = "# [⚖ A©tor Declaration]"
USER_CONTEXT = "A©t0r"

# Константы среды
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
PRIMARY_DIR = r"F:\Мой диск\PDF_Links"
FALLBACK_DIR = r"H:\ACTOR_DEV_ENV\PDF_Links"
NORTHSTAR_EXE = r"C:\Users\arhiv\Downloads\Downolde\northstar-1.0.7-windows-x86_64\northstar-1.0.7-windows-x86_64\app\northstar-ui.exe"


def sanitize_filename(name):
    clean = re.sub(r'[<>:"/\\|?*]', "_", name).strip()
    return clean[:120]


def get_target_dir():
    for d in [PRIMARY_DIR, FALLBACK_DIR]:
        try:
            os.makedirs(d, exist_ok=True)
            test_file = os.path.join(d, ".actor_test")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("test")
            os.remove(test_file)
            return d
        except Exception as e:
            print(f"[{USER_CONTEXT}] Директория {d} недоступна: {e}")
    return FALLBACK_DIR


TARGET_DIR = get_target_dir()
MANIFEST_PATH = os.path.join(TARGET_DIR, "pdf_index.json")
PRIV_KEY_PATH = os.path.join(TARGET_DIR, "actor_ed25519.pem")


def calculate_stream_sha256(stream):
    hasher = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(8192), b""):
        hasher.update(chunk)
    stream.seek(0)
    return hasher.hexdigest()


def calculate_file_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_merkle_root(hash_list):
    if not hash_list:
        return None
    current_layer = sorted(hash_list)
    while len(current_layer) > 1:
        next_layer = []
        for i in range(0, len(current_layer), 2):
            left = current_layer[i]
            right = (
                current_layer[i + 1] if i + 1 < len(current_layer) else current_layer[i]
            )
            combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
            next_layer.append(combined)
        current_layer = next_layer
    return current_layer[0]


def load_or_generate_ed25519():
    if os.path.exists(PRIV_KEY_PATH):
        with open(PRIV_KEY_PATH, "rb") as f:
            priv_key = serialization.load_pem_private_key(f.read(), password=None)
    else:
        print(f"[{USER_CONTEXT}] Генерация новой ключевой пары Ed25519...")
        priv_key = ed25519.Ed25519PrivateKey.generate()
        with open(PRIV_KEY_PATH, "wb") as f:
            f.write(
                priv_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
    return priv_key


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "entries" not in data:
                    return {"entries": data, "cryptography": {}}
                return data
            except json.JSONDecodeError:
                pass
    return {"entries": {}, "cryptography": {}}


def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)


def main():
    print(f"[{USER_CONTEXT}] Целевая директория: {TARGET_DIR}")
    manifest = load_manifest()
    priv_key = load_or_generate_ed25519()

    creds = None
    token_path = r"H:\ACTOR_DEV_ENV\token.json"
    cred_path = r"H:\ACTOR_DEV_ENV\credentials.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(cred_path):
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        else:
            print(
                f"[{USER_CONTEXT}] credentials.json не найден. Работа в режиме оффлайн/демонстрации."
            )
            creds = None

    service = None
    if creds:
        service = build("drive", "v3", credentials=creds)

    print(f"[{USER_CONTEXT}] Синхронизация манифеста файлов...")
    items = []
    if service:
        try:
            results = (
                service.files()
                .list(
                    q="mimeType='application/pdf'",
                    pageSize=50,
                    fields="nextPageToken, files(id, name, webViewLink)",
                )
                .execute()
            )
            items = results.get("files", [])
        except Exception as e:
            print(f"[{USER_CONTEXT}] Google Drive API error: {e}")

    updated = False

    if not items:
        print(
            f"[{USER_CONTEXT}] Облачные файлы не обнаружены. Режим локальной демонстрации из репозитория..."
        )
        import glob

        local_pdfs = glob.glob(r"H:\ACTOR_DEV_ENV/**/*.pdf", recursive=True)
        for pdf_path in local_pdfs[:20]:
            file_name = os.path.basename(pdf_path)
            base_name = sanitize_filename(os.path.splitext(file_name)[0])
            cmd_path = os.path.join(TARGET_DIR, f"{base_name}.cmd")
            img_path = os.path.join(TARGET_DIR, f"{base_name}.jpg")
            file_id = f"local_{base_name}"

            is_in_manifest = file_id in manifest["entries"]
            cmd_exists = os.path.exists(cmd_path)
            img_exists = os.path.exists(img_path)

            if cmd_exists and img_exists and is_in_manifest:
                print(f"[{USER_CONTEXT}] Пропуск (индексировано): {file_name}")
                continue

            updated = True
            if not cmd_exists:
                web_link = f"file:///{pdf_path.replace(os.sep, '/')}"
                cmd_content = (
                    f'{A©TOR_KEY}\n@echo off\nstart "" "{NORTHSTAR_EXE}" "{web_link}"'
                )
                with open(cmd_path, "w", encoding="utf-8") as f:
                    f.write(cmd_content)

            print(f"[{USER_CONTEXT}] Обработка локального потока: {file_name}")
            with open(pdf_path, "rb") as pf:
                fh = io.BytesIO(pf.read())

            pdf_sha256 = calculate_stream_sha256(fh)

            if not img_exists:
                try:
                    doc = fitz.open(stream=fh, filetype="pdf")
                    if len(doc) > 0:
                        page = doc.load_page(0)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        img = Image.frombytes(
                            "RGB", [pix.width, pix.height], pix.samples
                        )
                        img.save(img_path, "JPEG", quality=85)
                    doc.close()
                except Exception as e:
                    print(f"[{USER_CONTEXT}] Ошибка рендеринга {file_name}: {e}")
            fh.close()

            manifest["entries"][file_id] = {
                "document": {
                    "name": file_name,
                    "cloud_url": f"file:///{pdf_path.replace(os.sep, '/')}",
                    "original_pdf_sha256": pdf_sha256,
                },
                "local_assets": {
                    "cmd_launcher": {
                        "file": f"{base_name}.cmd",
                        "sha256": calculate_file_sha256(cmd_path),
                    },
                    "preview_image": {
                        "file": f"{base_name}.jpg",
                        "sha256": calculate_file_sha256(img_path),
                    },
                },
            }
    else:
        for item in items:
            file_id = item["id"]
            file_name = item["name"]
            web_link = item.get("webViewLink", "")

            base_name = sanitize_filename(os.path.splitext(file_name)[0])
            cmd_path = os.path.join(TARGET_DIR, f"{base_name}.cmd")
            img_path = os.path.join(TARGET_DIR, f"{base_name}.jpg")

            is_in_manifest = file_id in manifest["entries"]
            cmd_exists = os.path.exists(cmd_path)
            img_exists = os.path.exists(img_path)

            if cmd_exists and img_exists and is_in_manifest:
                print(f"[{USER_CONTEXT}] Пропуск (индексировано): {file_name}")
                continue

            updated = True
            if not cmd_exists:
                cmd_content = (
                    f'{A©TOR_KEY}\n@echo off\nstart "" "{NORTHSTAR_EXE}" "{web_link}"'
                )
                with open(cmd_path, "w", encoding="utf-8") as f:
                    f.write(cmd_content)

            print(
                f"[{USER_CONTEXT}] Потоковая загрузка в RAM и хэширование: {file_name}"
            )
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            pdf_sha256 = calculate_stream_sha256(fh)

            if not img_exists:
                try:
                    doc = fitz.open(stream=fh, filetype="pdf")
                    page = doc.load_page(0)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img.save(img_path, "JPEG", quality=85)
                    doc.close()
                except Exception as e:
                    print(f"[{USER_CONTEXT}] Ошибка рендеринга для {file_name}: {e}")

            fh.close()

            manifest["entries"][file_id] = {
                "document": {
                    "name": file_name,
                    "cloud_url": web_link,
                    "original_pdf_sha256": pdf_sha256,
                },
                "local_assets": {
                    "cmd_launcher": {
                        "file": f"{base_name}.cmd",
                        "sha256": calculate_file_sha256(cmd_path),
                    },
                    "preview_image": {
                        "file": f"{base_name}.jpg",
                        "sha256": calculate_file_sha256(img_path),
                    },
                },
            }

    needs_signing = (
        updated
        or not manifest.get("cryptography")
        or "manifest_payload_sha256" not in manifest.get("cryptography", {})
    )
    if needs_signing:
        print(
            f"[{USER_CONTEXT}] Вычисление Merkle Root, Manifest Payload Hash и генерация подписи Ed25519..."
        )
        all_pdf_hashes = [
            entry["document"]["original_pdf_sha256"]
            for entry in manifest["entries"].values()
        ]
        merkle_root = compute_merkle_root(all_pdf_hashes)

        if merkle_root:
            canonical_entries_bytes = json.dumps(
                manifest["entries"], sort_keys=True, ensure_ascii=False
            ).encode("utf-8")
            manifest_payload_sha256 = hashlib.sha256(
                canonical_entries_bytes
            ).hexdigest()
            entries_sha256 = manifest_payload_sha256  # alias for compatibility

            signed_payload = f"{merkle_root}:{manifest_payload_sha256}".encode("utf-8")
            signature = priv_key.sign(signed_payload)
            pub_key = priv_key.public_key()
            pub_bytes_hex = pub_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            ).hex()

            manifest["cryptography"] = {
                "manifest_payload_sha256": manifest_payload_sha256,
                "merkle_root_sha256": merkle_root,
                "entries_sha256": entries_sha256,
                "signature_ed25519_hex": signature.hex(),
                "public_key_ed25519_hex": pub_bytes_hex,
                "signature_payload": "merkle_root_sha256:manifest_payload_sha256",
            }
            save_manifest(manifest)
            print(
                f"[{USER_CONTEXT}] Манифест успешно подписан. Manifest Payload Hash: {manifest_payload_sha256}"
            )
    else:
        print(
            f"[{USER_CONTEXT}] Изменений не обнаружено. Структура Меркла и хэш манифеста актуальны."
        )


if __name__ == "__main__":
    main()
