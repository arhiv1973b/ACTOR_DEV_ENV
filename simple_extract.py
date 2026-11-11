import fitz
import sys


def extract_text(pdf_path, output_path):
    try:
        text_content = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_content += page.get_text() + "\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"[+] Успешно извлечен текст в {output_path}")
    except Exception as e:
        print(f"[-] Ошибка: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python simple_extract.py <input_pdf> <output_txt>")
        sys.exit(1)
    extract_text(sys.argv[1], sys.argv[2])
