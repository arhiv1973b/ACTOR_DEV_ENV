import os

pdf_path = r"H:\Загрузки\Aviza..pdf"
text = ""

try:
    import fitz  # PyMuPDF

    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
except Exception as e:
    print(f"PyMuPDF error: {e}")
    try:
        from pypdf import PdfReader

        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e2:
        print(f"pypdf error: {e2}")

print("--- EXTRACTED TEXT FROM AVIZA..PDF ---")
print(text)
with open(r"H:\ACTOR_DEV_ENV\aviza_extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
