import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# --- КОНФИГУРАЦИЯ ---
EVIDENCE_DIR = r"H:\ACTOR_DEV_ENV\evidence"
TESSERACT_LANG = "ron+rus+eng"  # Поддержка всех языков документации
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Путь по умолчанию после choco install

# Настройка пути к Tesseract для pytesseract
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

LEGAL_FOOTER = """

--------------------------------------------------
[VERIFIED VIA OCR ZERO-BYPASS PIPELINE]
Jurisdiction: Universal Declaration of Human Rights (UDHR) & Art. 4 of the Constitution of the Republic of Moldova.
Status: Peremptory norms execution (jus cogens) / Erga Omnes.
A©TOR_KEY="# [⚖ A©tor Declaration]"
--------------------------------------------------"""


def process_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    ocr_triggered = False

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()

        # Если текста меньше 50 символов - текстового слоя нет, это скан
        if len(text) < 50:
            # Рендеринг страницы в высоком разрешении (300 DPI) для OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang=TESSERACT_LANG).strip()
            ocr_triggered = True

        full_text += f"\n--- Page {page_num + 1} ---\n{text}\n"

    return full_text.strip(), ocr_triggered


def main():
    print("=== ЗАПУСК УНИВЕРСАЛЬНОГО OCR-ПАЙПЛАЙНА (PyMuPDF + Tesseract) ===")

    if not os.path.exists(EVIDENCE_DIR):
        print(f"[X] Директория не найдена: {EVIDENCE_DIR}")
        return

    for filename in os.listdir(EVIDENCE_DIR):
        file_path = os.path.join(EVIDENCE_DIR, filename)

        # Проверяем PDF-файлы и симлинки, ведущие на PDF
        if filename.lower().endswith(".pdf"):
            print(f"[*] Обработка: {filename} ... ", end="")
            try:
                text, used_ocr = process_pdf(file_path)

                if text:
                    text += LEGAL_FOOTER
                    out_path = os.path.join(EVIDENCE_DIR, f"{filename}.txt")

                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)

                    method = "Tesseract OCR" if used_ocr else "PyMuPDF (Text Layer)"
                    print(f"УСПЕХ ({method})")
                else:
                    print("ОШИБКА (пустой результат)")
            except Exception as e:
                print(f"СБОЙ: {str(e)}")

    print("\n=== ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО ===")
    print(
        "Не забудьте запустить `python generate_integrity_witness.py` для обновления манифестов."
    )


if __name__ == "__main__":
    main()
