import os
import sys
import hashlib
import json
import argparse
import logging
from datetime import datetime
from urllib.parse import urlparse
import concurrent.futures
import requests
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# Настройка Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Логирование
log_file = r"H:\ACTOR_DEV_ENV\ocr_pipeline.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)


def fetch_from_url(url, outdir):
    os.makedirs(outdir, exist_ok=True)
    logging.info(f"Downloading file from URL: {url}")
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            raise Exception(f"Download failed with status code: {r.status_code}")

        parsed_url = urlparse(url)
        fname = os.path.basename(parsed_url.path) or "downloaded_file"
        if "." not in fname:
            fname += ".png"

        sha256 = hashlib.sha256(r.content).hexdigest()
        local_path = os.path.join(outdir, f"{sha256[:8]}_{fname}")

        with open(local_path, "wb") as f:
            f.write(r.content)

        logging.info(
            f"Successfully downloaded {url} -> {local_path} (SHA256: {sha256})"
        )
        return local_path, sha256
    except Exception as e:
        logging.error(f"Error fetching URL {url}: {e}")
        raise


def ocr_image(image_path_or_pil, lang="rus+eng+ron"):
    try:
        if isinstance(image_path_or_pil, str):
            img = Image.open(image_path_or_pil)
        else:
            img = image_path_or_pil
        text = pytesseract.image_to_string(img, lang=lang)
        return text
    except Exception as e:
        logging.error(f"OCR error: {e}")
        return f"[OCR ERROR: {str(e)}]"


def process_pdf(pdf_path, output_dir, lang="rus+eng+ron", dpi=300):
    logging.info(f"Processing PDF: {pdf_path}")
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        logging.info(f"Rendering page {page_num + 1}/{len(doc)}")
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        img_path = os.path.join(output_dir, f"{base_name}_page_{page_num + 1}.png")
        pix.save(img_path)

        page_text = ocr_image(img_path, lang=lang)
        full_text += f"\n--- Page {page_num + 1} ---\n" + page_text

    doc.close()
    return full_text


def process_file(target_input, outdir, lang, dpi):
    source_url = None
    file_path = target_input

    if target_input.startswith("http://") or target_input.startswith("https://"):
        source_url = target_input
        try:
            file_path, pre_sha256 = fetch_from_url(target_input, outdir)
        except Exception as e:
            logging.error(f"Failed to process URL {target_input}: {e}")
            return {"path": target_input, "status": "DOWNLOAD_ERROR", "error": str(e)}

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return {"path": file_path, "status": "FILE_NOT_FOUND"}

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    file_hash = sha256.hexdigest()
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(file_path)[1].lower()

    os.makedirs(outdir, exist_ok=True)
    extracted_text = ""

    if ext == ".pdf":
        extracted_text = process_pdf(file_path, outdir, lang=lang, dpi=dpi)
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
        extracted_text = ocr_image(file_path, lang=lang)
    else:
        extracted_text = "[Unsupported file format for OCR]"
        logging.warning(f"Unsupported file format: {ext}")

    out_txt_path = os.path.join(
        outdir, f"{os.path.basename(file_path)}_{file_hash[:8]}.txt"
    )
    with open(out_txt_path, "w", encoding="utf-8") as tf:
        tf.write(extracted_text)

    logging.info(f"File processed: {file_path}, SHA256={file_hash}, size={file_size}")

    anomalies = summarize_anomalies(extracted_text)
    semantics = extract_semantics(extracted_text)

    result = {
        "path": file_path,
        "filename": os.path.basename(file_path),
        "sha256": file_hash,
        "size_bytes": file_size,
        "extracted_text_path": out_txt_path,
        "extracted_text_snippet": extracted_text[:500],
        "status": "success",
        "anomalies_summary": anomalies,
        "semantics_vector": semantics,
    }

    if source_url:
        result["source_url"] = source_url

    return result


def summarize_anomalies(text):
    anomalies = []
    if "?" in text or "[]" in text:
        anomalies.append("Garbled symbols detected")
    if any(char in text for char in ["ţ", "ş"]):
        anomalies.append("Diacritic confusion (cedilla/comma-below)")
    if len(text.strip()) < 50:
        anomalies.append("Very low text density")
    return anomalies


def extract_semantics(text):
    """Извлечение смысловых векторов и ключевых юридических/финансовых маркеров дела."""
    vectors = {
        "has_idnp": "2000001159655" in text,
        "has_sum_mdl": "25 210" in text or "25210" in text,
        "transliteration_collision": "MACHERET" in text or "MACERET" in text,
        "philology_aviz": "269" in text or "Aviz" in text,
        "key_entities_detected": [],
    }

    keywords = [
        "Maceret",
        "Macheret",
        "IDNP",
        "MDL",
        "Aviz",
        "SWIFT",
        "KYC",
        "Judecatoria",
        "Banca",
    ]
    for kw in keywords:
        if kw.lower() in text.lower():
            vectors["key_entities_detected"].append(kw)

    return vectors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parallel Multi-URL OCR Pipeline with PyMuPDF + Tesseract & Semantics"
    )
    parser.add_argument(
        "inputs", nargs="+", help="Paths to files or URLs to OCR (supports multiple)"
    )
    parser.add_argument(
        "--lang", default="rus+eng+ron", help="Languages for OCR (default: rus+eng+ron)"
    )
    parser.add_argument(
        "--outdir",
        default=r"H:\ACTOR_DEV_ENV\analysis_temp\ocr_pipeline_output",
        help="Output directory",
    )
    parser.add_argument(
        "--dpi", type=int, default=300, help="Rendering DPI for PDF pages"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="Max parallel workers for batch processing",
    )
    args = parser.parse_args()

    print(f"=== Parallel OCR Pipeline (Workers: {args.workers}) ===")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_input = {
            executor.submit(process_file, inp, args.outdir, args.lang, args.dpi): inp
            for inp in args.inputs
        }
        for future in concurrent.futures.as_completed(future_to_input):
            inp = future_to_input[future]
            try:
                res = future.result()
                results.append(res)
                logging.info(f"Completed processing for: {inp}")
            except Exception as e:
                logging.error(f"Task generated an exception for {inp}: {e}")
                results.append({"path": inp, "status": "EXCEPTION", "error": str(e)})

    print(json.dumps(results, indent=2, ensure_ascii=False))
