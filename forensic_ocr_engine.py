import pytesseract
from PIL import Image
import os
import sys

# ЗАПРЕТ НА ANSI/EN CODING: Принудительное использование UTF-8
# Используем модели 'rus+ron' и отключаем английский язык
TESSERACT_CONFIG = r'--oem 3 --psm 6 -l rus+ron -c tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

def forensic_ocr(image_path):
    """
    Forensic OCR: Работа через PIL для исключения зависимостей cv2.
    """
    print(f"[*] Анализ файла: {image_path}")
    
    # Открытие изображения
    img = Image.open(image_path)
    
    # Прямое распознавание
    text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
    
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[!] Ошибка: Не указан путь к файлу.")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    result = forensic_ocr(file_path)
    
    print("\n--- РЕЗУЛЬТАТ РАСПОЗНАВАНИЯ (UTF-8) ---")
    print(result)
    print("----------------------------------------")
    
    # Сохранение результата
    output_file = file_path + "_ocr_result.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"[*] Результат зафиксирован в: {output_file}")
