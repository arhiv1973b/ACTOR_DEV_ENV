import os
import sys
import json
import zipfile
from io import BytesIO

try:
    from PIL import Image
    import pytesseract
    from pillow_heif import register_heif_opener
    
    # Регистрируем поддержку HEIC для Pillow на уровне движка
    register_heif_opener()
except ImportError:
    print("[-] Ошибка: Отсутствуют необходимые библиотеки.")
    print("[-] Выполните в терминале: pip install Pillow pytesseract pillow-heif")
    sys.exit(1)

# Настройка путей Tesseract для Windows
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\arhiv\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
]

tesseract_found = False
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        break

if not tesseract_found:
    print("[!] Внимание: tesseract.exe не найден в стандартных путях.")

def find_archive():
    print("[*] Поиск архива iCloud...")
    
    # Прямые директории для сканирования (с учетом неразрывных пробелов от Apple)
    search_dirs = [
        r"C:\Users\arhiv\Downloads\Downolde",
        r"C:\Users\arhiv\Downloads",
        r"H:\Загрузки",
        r"H:\arhiv_archive"
    ]
    
    for d in search_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                # Ищем архивы от Apple, игнорируя проблемы с кодировкой пробелов
                if 'iCloud' in f and f.lower().endswith('.zip'):
                    path = os.path.join(d, f)
                    print(f"[+] Найден целевой архив: {path}")
                    return path
                    
    return None

def process_archive(zip_path, output_json="ocr_manifest.json"):
    ocr_results = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            # Расширенный список форматов, включая .heic
            image_files = [f for f in z.namelist() if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.heic'))]
            print(f"[*] В архиве найдено изображений: {len(image_files)} (обработка в памяти)")
            
            for img_name in image_files:
                print(f"[*] Распознавание (rus+ron+eng): {img_name}...")
                try:
                    with z.open(img_name) as file_obj:
                        # pillow-heif автоматически перехватит формат HEIC
                        img = Image.open(BytesIO(file_obj.read()))
                        
                        # Принудительная конвертация в RGB, чтобы избежать ошибок Tesseract с альфа-каналами
                        if img.mode not in ('L', 'RGB'):
                            img = img.convert('RGB')
                            
                        # Извлечение текста (русский, румынский, английский)
                        text = pytesseract.image_to_string(img, lang='rus+ron+eng').strip()
                        
                        # Сохраняем в любом случае, даже если текст пустой, для статистики
                        ocr_results.append({
                            "filename": img_name,
                            "char_count": len(text),
                            "text": text
                        })
                except Exception as e:
                    print(f"[-] Ошибка при обработке файла {img_name}: {e}")
                    
    except Exception as e:
        print(f"[-] Ошибка при чтении zip-архива {zip_path}: {e}")
        return
        
    out_path = os.path.abspath(output_json)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=4)
        
    print(f"[+] Готово! Сгенерирован OCR-манифест: {out_path}")
    print(f"[+] Всего обработано файлов: {len(ocr_results)}")
    
    # Вывод краткой статистики
    non_empty = sum(1 for item in ocr_results if item['char_count'] > 10)
    print(f"[*] Изображений со значимым текстом (>10 символов): {non_empty}")

if __name__ == "__main__":
    archive_path = find_archive()
    if archive_path:
        process_archive(archive_path)
    else:
        print("[-] Архив не найден. Проверьте папку C:\\Users\\arhiv\\Downloads\\Downolde")
