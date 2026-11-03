import os
import shutil
import fitz  # PyMuPDF
import subprocess

pdf_path = r"Revizion.pdf"
backup_dir = r"Safe_Backup"
output_txt = r"Revizion_OCR.txt"

# Шаг 1: Бэкап и Изоляция
os.makedirs(backup_dir, exist_ok=True)
if os.path.exists(pdf_path):
    shutil.copy(pdf_path, os.path.join(backup_dir, "Revizion.pdf"))
    print("Backup created successfully.")
else:
    print(f"Source PDF not found at {pdf_path}")

# Шаг 3: Альтернативный OCR через PyMuPDF (и извлечение текста)
text_content = ""
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        if not page_text.strip():
            # Если текст пустой, пробуем pytesseract если доступно
            try:
                import pytesseract
                from PIL import Image

                pix = page.get_pixmap()
                img_path = f"temp_page_{page_num}.png"
                pix.save(img_path)
                page_text = pytesseract.image_to_string(
                    Image.open(img_path), lang="ron+rus+eng"
                )
                os.remove(img_path)
            except Exception as e:
                page_text = f"[OCR Failed for page {page_num}: {e}]"
        text_content += f"\n--- Page {page_num + 1} ---\n" + page_text

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(text_content)
    print(f"Text extracted and saved to {output_txt}")
