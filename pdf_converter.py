from pdf2image import convert_from_path
import sys

def convert_pdf_page(pdf_path, output_image_path):
    # Конвертируем только первую страницу
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    pages[0].save(output_image_path, 'JPEG')
    print(f"[*] Страница сохранена как: {output_image_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_converter.py <pdf_path> <output_image_path>")
        sys.exit(1)
    convert_pdf_page(sys.argv[1], sys.argv[2])
