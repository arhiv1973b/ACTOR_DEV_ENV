import os
import sys
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import easyocr
import pypdf

# Initialize EasyOCR reader for Russian and English (Cyrillic-compatible)
print("[*] Initializing EasyOCR reader (ru, en)...")
reader = easyocr.Reader(["ru", "en"], gpu=False)


def extract_text_from_image(image_path):
    print(f"[*] Running OCR on image: {image_path}")
    try:
        results = reader.readtext(image_path)
        text_lines = [res[1] for res in results]
        return "\n".join(text_lines)
    except Exception as e:
        return f"[OCR ERROR: {str(e)}]"


def extract_text_from_pdf(pdf_path):
    print(f"[*] Extracting text from PDF: {pdf_path}")
    text = ""
    try:
        pdf_reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {i + 1} ---\n" + page_text
        if not text.strip():
            text = "[PDF appears scanned or empty of direct text]"
    except Exception as e:
        text = f"[PDF ERROR: {str(e)}]"
    return text


def process_file(file_path):
    if not os.path.exists(file_path):
        return {"path": file_path, "status": "FILE_NOT_FOUND"}

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    file_hash = sha256.hexdigest()
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    extracted_text = ""
    if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        extracted_text = extract_text_from_image(file_path)
    elif ext == ".pdf":
        extracted_text = extract_text_from_pdf(file_path)
    else:
        extracted_text = "[Unsupported file type for automated OCR/text extraction]"

    os.makedirs(r"H:\ACTOR_DEV_ENV\analysis_temp\ocr_extracted", exist_ok=True)
    out_txt_path = os.path.join(
        r"H:\ACTOR_DEV_ENV\analysis_temp\ocr_extracted",
        f"{os.path.basename(file_path)}_{file_hash[:8]}.txt",
    )
    with open(out_txt_path, "w", encoding="utf-8") as tf:
        tf.write(extracted_text)

    return {
        "path": file_path,
        "filename": os.path.basename(file_path),
        "sha256": file_hash,
        "size_bytes": file_size,
        "extracted_text_path": out_txt_path,
        "extracted_text_snippet": extracted_text[:500],
        "status": "success",
    }


if __name__ == "__main__":
    print("=== TI-ULA Evidence OCR & Text Extraction Tool ===")
    if len(sys.argv) > 1:
        target = sys.argv[1]
        res = process_file(target)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python extract_and_ocr_evidence.py <file_path>")
