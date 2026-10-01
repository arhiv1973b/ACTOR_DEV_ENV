import os
import sys
import json

try:
    import fitz  # PyMuPDF
except ImportError:
    print("[-] Ошибка: Отсутствует библиотека PyMuPDF.")
    sys.exit(1)

SEARCH_DIRS = [
    r"H:\ACTOR_DEV_ENV"
]

OUTPUT_JSON = "pdf_manifest.json"

def find_pdfs():
    pdf_files = []
    for d in SEARCH_DIRS:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                # Skip hidden or virtual env dirs
                if any(p in root for p in ['.venv', '.git', 'node_modules', '.native', '.crush']):
                    continue
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))
    return list(set(pdf_files))

def process_pdfs(pdf_paths):
    results = []
    print(f"[*] Найдено PDF-документов в рабочей директории: {len(pdf_paths)}")
    
    out_path = os.path.abspath(OUTPUT_JSON)
    
    for idx, path in enumerate(pdf_paths):
        filename = os.path.basename(path)
        print(f"[{idx+1}/{len(pdf_paths)}] Чтение: {filename}...")
        
        text_content = ""
        try:
            with fitz.open(path) as doc:
                for page in doc:
                    text_content += page.get_text() + "\n"
                    
            text_content = text_content.strip()
            
            results.append({
                "filename": filename,
                "file_path": path,
                "char_count": len(text_content),
                "text": text_content
            })
        except Exception as e:
            print(f"[-] Ошибка при чтении {filename}: {e}")
            
        # Save incrementally every 50 files
        if (idx + 1) % 50 == 0 or (idx + 1) == len(pdf_paths):
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"[+] Прогресс сохранен в {out_path} ({idx+1} файлов)")
            
    print(f"[+] Готово! Сгенерирован манифест: {out_path}")

if __name__ == "__main__":
    pdfs = find_pdfs()
    if pdfs:
        process_pdfs(pdfs)
    else:
        print("[-] PDF-документы не найдены.")
