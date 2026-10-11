import os
import hashlib
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import json

# путь к бинарнику Tesseract
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def ocr_pdf(pdf_path, outdir="ocr_output", dpi=300, lang="rus+ron+eng"):
    os.makedirs(outdir, exist_ok=True)
    results = []

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            results.append(
                {"page": page_num + 1, "text": text, "source": "pymupdf_text_layer"}
            )
        else:
            images = convert_from_path(
                pdf_path, dpi=dpi, first_page=page_num + 1, last_page=page_num + 1
            )
            for img in images:
                ocr_data = pytesseract.image_to_string(img, lang=lang)
                results.append(
                    {"page": page_num + 1, "text": ocr_data, "source": "tesseract_ocr"}
                )

    out_json = os.path.join(outdir, os.path.basename(pdf_path) + ".json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(
            {"file": pdf_path, "sha256": sha256_file(pdf_path), "pages": results},
            f,
            ensure_ascii=False,
            indent=2,
        )

    return out_json


if __name__ == "__main__":
    print("OCR utility ready under A©tor jurisdiction.")
