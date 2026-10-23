# ocr_module.py – OCR/TrOCR integration for TI‑ULA
# -*- coding: utf-8 -*-
"""OCR module

This script processes image and PDF files, extracts text with Tesseract (or TrOCR via 🤗 Transformers),
creates a semantic embedding using LangChain + HuggingFace transformer, and sends the result to the
local MCP server (orchestrator_v13.py) via a JSON‑RPC‑like socket call.

Features:
- Handles single files or a directory (recursively).
- Detects printed vs. handwritten text (simple heuristic based on filename suffix).
- Uses `pytesseract` for OCR; if `torch`‑based TrOCR model is available it can be swapped.
- Generates an embedding with `SentenceTransformer` via LangChain.
- Sends a payload:
    {
        "action": "store",
        "key": "<sha256-of-file>",
        "vector": <list‑of‑float>,
        "meta": {
            "source": "printed|handwritten",
            "path": "<original‑path>",
            "author": "A©tor",
            "timestamp": "<ISO‑8601>"
        }
    }
"""

import argparse
import hashlib
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import fitz  # PyMuPDF for native PDF text extraction

# ---------- OCR ----------
try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    print("[Ошибка] pytesseract не установлен. Установите зависимости из requirements.txt", e)
    sys.exit(1)

# Optional TrOCR support – uses a transformer model from 🤗
USE_TROCR = False
if USE_TROCR:
    try:
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    except Exception as e:
        print("[WARN] TrOCR импорт не удался, будет использован pytesseract", e)
        USE_TROCR = False

# ---------- Embedding ----------
try:
    from langchain.embeddings import HuggingFaceEmbeddings
except Exception as e:
    print("[Ошибка] LangChain embeddings не доступны. Установите dependencies.", e)
    sys.exit(1)

# Initialise embedding model (small, CPU‑friendly)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ---------- Utility functions ----------

def calculate_sha256(file_path: Path) -> str:
    """Return hex SHA‑256 of a file (read in chunks)."""
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_text_from_image(image_path: Path) -> str:
    """Run pytesseract on an image file."""
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang="eng+rus")

def extract_text_from_pdf(pdf_path: Path) -> list:
    """Tiered extraction: native PDF text first, OCR as fallback for low‑text pages.
    Returns a list of dicts: {"page": int, "text": str, "source": "native"|"ocr"}.
    """
    doc = fitz.open(str(pdf_path))
    results = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Попытка извлечь native‑текст
        native_text = page.get_text("text").strip()
        if len(native_text) < 50:
            # Недостаточно текста – используем OCR
            print(f"[WARN] Страница {page_num+1} имеет мало текста, запускаю OCR...")
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ocr_text = pytesseract.image_to_string(img, lang="eng+rus")
            results.append({"page": page_num + 1, "text": ocr_text, "source": "ocr"})
        else:
            results.append({"page": page_num + 1, "text": native_text, "source": "native"})
    return results

def generate_embedding(text: str):
    """Return a list of floats – the embedding vector."""
    return embeddings.embed_query(text)

def send_to_mcp(key: str, vector, meta: dict):
    payload = {
        "action": "store",
        "key": key,
        "vector": vector,
        "meta": meta,
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 5000))
            s.sendall(json.dumps(payload).encode("utf-8"))
            resp_raw = s.recv(4096).decode("utf-8")
            resp = json.loads(resp_raw)
            return resp
    except Exception as e:
        return {"error": str(e)}

def process_file(file_path: Path):
    ext = file_path.suffix.lower()
    # Simple heuristic: filename ending with "_hand" → handwritten
    source_type = "handwritten" if "hand" in file_path.stem.lower() else "printed"

    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}:
        # Single image processing
        text = extract_text_from_image(file_path)
        if not text.strip():
            print(f"[WARN] Пустой результат OCR для {file_path}")
            return
        vector = generate_embedding(text)
        sha = calculate_sha256(file_path)
        meta = {
            "source": source_type,
            "path": str(file_path),
            "author": "A©tor",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        resp = send_to_mcp(sha, vector, meta)
        print(f"[ОК] {file_path} → {resp.get('status', resp.get('error'))}")
    elif ext == ".pdf":
        # PDF – process each page separately
        try:
            from pdf2image import convert_from_path
        except ImportError:
            print("[WARN] pdf2image не установлен – невозможно обработать PDF")
            return
        pages = convert_from_path(str(file_path), fmt="png")
        for i, page_img in enumerate(pages, start=1):
            text = pytesseract.image_to_string(page_img, lang="eng+rus")
            if not text.strip():
                print(f"[WARN] Пустой результат OCR для страницы {i} в {file_path}")
                continue
            vector = generate_embedding(text)
            sha = calculate_sha256(file_path) + f"_page_{i}"
            meta = {
                "source": source_type,
                "path": str(file_path),
                "page": i,
                "author": "A©tor",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            resp = send_to_mcp(sha, vector, meta)
            print(f"[ОК] {file_path} (стр. {i}) → {resp.get('status', resp.get('error'))}")
    else:
        print(f"[СКИП] Не поддерживаемый тип: {file_path}")
        return

def walk_and_process(root: Path):
    for p in root.rglob("*.*"):
        if p.is_file():
            process_file(p)

def main():
    parser = argparse.ArgumentParser(description="OCR → MCP bridge for TI‑ULA")
    parser.add_argument("input", type=str, help="Путь к файлу или директории")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"[ERROR] Путь не найден: {input_path}")
        sys.exit(1)

    if input_path.is_dir():
        walk_and_process(input_path)
    else:
        process_file(input_path)

if __name__ == "__main__":
    main()
