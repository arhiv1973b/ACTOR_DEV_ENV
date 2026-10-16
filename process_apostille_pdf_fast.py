import fitz
import pytesseract
from PIL import Image
import io
import os

pdf_path = r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila (2).pdf"
output_pdf_path = r"H:\ACTOR_DEV_ENV\apostille_80UQ636YBZG17_2013073978518.pdf"

doc = fitz.open(pdf_path)
pdf_writer = fitz.open()

for page_num in range(len(doc)):
    page = doc[page_num]
    if page_num == 0:
        # Keep first page as is
        pdf_writer.insert_pdf(doc, from_page=0, to_page=0)
        continue

    # For second page onwards, render image and do OCR text layer
    pix = page.get_pixmap(dpi=150)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension="pdf", lang="ron")
    ocr_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pdf_writer.insert_pdf(ocr_doc)

pdf_writer.save(output_pdf_path)
print(f"Generated searchable PDF at {output_pdf_path}")
