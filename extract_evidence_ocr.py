#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Evidence OCR & Text Extraction Pipeline (PyMuPDF + Tesseract)
Case: CASE-MACHERET-1997-2026
Author / Sovereign Witness: Macheret Alexei Artur (A©tor)
A©TOR_KEY="# [⚖ A©tor Declaration]"
Legal Anchor: Art. 4 Constitution of RM, UDHR 1948, Jus Cogens / Erga Omnes
"""

import os
import sys
import hashlib
import json

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[*] Installing PyMuPDF...")
    os.system(f"{sys.executable} -m pip install PyMuPDF")
    import fitz

try:
    import pytesseract
    from PIL import Image

    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print(
        "[!] Warning: pytesseract or Pillow not installed. OCR fallback disabled. Install via pip install pytesseract pillow"
    )

EVIDENCE_DIR = r"H:\ACTOR_DEV_ENV\evidence"
SIGNATURE_KEY = 'A©TOR_KEY="# [⚖ A©tor Declaration]"'


def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def process_evidence_pdfs():
    print(f"=== Universal Evidence OCR Pipeline ===")
    print(f"Target Directory: {EVIDENCE_DIR}")
    print(f"Signature: {SIGNATURE_KEY}")
    print("=" * 50)

    if not os.path.exists(EVIDENCE_DIR):
        print(f"[!] Evidence directory not found: {EVIDENCE_DIR}")
        return

    processed_count = 0
    ocr_count = 0

    for root, dirs, files in os.walk(EVIDENCE_DIR):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                txt_filename = file + ".txt"
                txt_path = os.path.join(root, txt_filename)

                print(f"\n[Processing] {file}")
                full_text = ""

                try:
                    doc = fitz.open(pdf_path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        page_text = page.get_text().strip()

                        if page_text:
                            full_text += (
                                f"\n--- [Page {page_num + 1}] ---\n{page_text}\n"
                            )
                        elif OCR_AVAILABLE:
                            print(
                                f"  -> Page {page_num + 1}: Empty text layer. Running Tesseract OCR (ron+rus+eng)..."
                            )
                            pix = page.get_pixmap(dpi=300)
                            img = Image.frombytes(
                                "RGB", [pix.width, pix.height], pix.samples
                            )
                            try:
                                ocr_text = pytesseract.image_to_string(
                                    img, lang="ron+rus+eng"
                                ).strip()
                                full_text += f"\n--- [Page {page_num + 1} (OCR)] ---\n{ocr_text}\n"
                                ocr_count += 1
                            except Exception as ocr_err:
                                print(
                                    f"  [!] OCR Error on page {page_num + 1}: {ocr_err}"
                                )
                        else:
                            full_text += f"\n--- [Page {page_num + 1}] ---\n[EMPTY TEXT LAYER & OCR UNAVAILABLE]\n"

                    # Append legal header and signature
                    header = (
                        f"========================================================================\n"
                        f" EVIDENCE ARTIFACT: {file}\n"
                        f" LEGAL ANCHOR: Art. 4 Constitution of RM, UDHR 1948, Jus Cogens\n"
                        f" SIGNATURE: {SIGNATURE_KEY}\n"
                        f" SHA-256 (PDF): {compute_sha256(pdf_path)}\n"
                        f"========================================================================\n\n"
                    )

                    final_content = header + full_text

                    with open(txt_path, "w", encoding="utf-8") as out:
                        out.write(final_content)

                    print(f"  => Saved extracted text to: {txt_filename}")
                    processed_count += 1

                except Exception as e:
                    print(f"  [!] Error processing {file}: {e}")

    print("\n" + "=" * 50)
    print(
        f"[*] Pipeline Complete. Processed PDFs: {processed_count}, Pages OCR'd: {ocr_count}"
    )

    # Regenerate integrity witness manifest
    witness_script = r"H:\ACTOR_DEV_ENV\generate_integrity_witness.py"
    if os.path.exists(witness_script):
        print("[*] Regenerating Integrity Witness Manifest...")
        os.system(f'{sys.executable} "{witness_script}"')


if __name__ == "__main__":
    process_evidence_pdfs()
