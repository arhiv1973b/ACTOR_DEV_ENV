# ocr_cli_bridge.py
# A©tor_KEY="# [⚖ A©tor Declaration]"
# Thin scan → raw-with-errors → process_ocr_to_udhr_pointer
# Does not clean OCR defects. Fingerprint contract stays in ocr_zero_weight_bridge.

import argparse
import os
import shutil

from PIL import Image
import pytesseract

from ocr_zero_weight_bridge import process_ocr_to_udhr_pointer

_WIN_TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.name == "nt" and os.path.isfile(_WIN_TESS):
    pytesseract.pytesseract.tesseract_cmd = _WIN_TESS
elif shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")


def main():
    parser = argparse.ArgumentParser(
        description="Zero-Weight OCR CLI Bridge with Defect Fingerprinting"
    )
    parser.add_argument("--image", required=True, help="Path to input image/scan")
    parser.add_argument("--drive-link", required=True, help="Google Drive link to original document")
    parser.add_argument("--output-name", required=True, help="Output identifier node name")
    parser.add_argument("--lang", default="rus+ron+eng", help="Tesseract languages")
    parser.add_argument("--psm", default="6", help="Tesseract PSM mode")
    parser.add_argument("--target-lang", default="en", help="Clean translation language label only")
    args = parser.parse_args()

    print(f"[*] Scanning image {args.image} with lang={args.lang}, psm={args.psm}...")
    image = Image.open(args.image)
    config = f"--oem 1 --psm {args.psm}"
    raw_text = pytesseract.image_to_string(image, lang=args.lang, config=config)

    raw_dir = os.path.join("🏛️_EVIDENCE", "OCR_TEXT_LAYER", "RAW_WITH_ERRORS")
    os.makedirs(raw_dir, exist_ok=True)
    raw_text_path = os.path.join(raw_dir, f"{args.output_name}_raw.txt")

    with open(raw_text_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    print(f"[+] Raw OCR text saved with typos to {raw_text_path}")
    process_ocr_to_udhr_pointer(
        args.drive_link, raw_text_path, args.output_name, target_lang=args.target_lang
    )


if __name__ == "__main__":
    main()
