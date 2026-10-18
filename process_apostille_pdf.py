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
    pix = page.get_pixmap(dpi=300)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))

    # OCR with pytesseract (romanian + russian + english)
    # Get pdf PDF bytes with text layer from tesseract
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(
        img, extension="pdf", lang="ron+rus+eng"
    )

    ocr_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pdf_writer.insert_pdf(ocr_doc)

pdf_writer.save(output_pdf_path)
print(f"Successfully generated OCR searchable PDF at {output_pdf_path}")
