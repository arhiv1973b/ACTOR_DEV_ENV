import os, sys, pytesseract
from pdf2image import convert_from_path

def ocr_extract(pdf_path):
    print(f"[OCR] Обработка: {pdf_path}")
    try:
        pages = convert_from_path(pdf_path, dpi=300)
        print(f"[OCR] Страниц найдено: {len(pages)}")
    except Exception as e:
        print(f"[ERROR] Ошибка при конвертации PDF: {e}")
        return
    
    full_text = ""
    for i, page in enumerate(pages, 1):
        print(f"[OCR] Распознавание страницы {i}...")
        text = pytesseract.image_to_string(page, lang="eng")
        full_text += f"\n{'='*60}\nСтраница {i}\n{'='*60}\n{text}\n"
    
    output_file = pdf_path + "_ocr_extracted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"[OCR] Результат сохранён: {output_file}")
    print(f"[OCR] Всего символов: {len(full_text)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ocr_extract(sys.argv[1])
    else:
        print("Использование: python ocr_pipeline.py <путь_к_pdf>")
