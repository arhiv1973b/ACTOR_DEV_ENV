#!/usr/bin/env python3
"""
File Access Bridge with OCR Support
Поддержка PDF через PyPDF + Tesseract OCR для сканированных документов
"""

import os
import sys
import json
import mimetypes
from pathlib import Path
from typing import Optional, Dict, List
import requests

class FileAccessBridgeWithOCR:
    """Управление доступом файлов с поддержкой OCR."""
    
    def __init__(self, base_paths: List[str] = None):
        self.base_paths = base_paths or [
            "F:\\Мой диск",
            "H:\\ACTOR_DEV_ENV",
            "C:\\temp",
            os.path.expanduser("~")
        ]
        self.ollama_url = "http://127.0.0.1:11434/api/generate"
    
    def is_safe_path(self, file_path: str) -> bool:
        """Проверить, что путь безопасен."""
        file_path = Path(file_path).resolve()
        for base in self.base_paths:
            try:
                file_path.relative_to(Path(base).resolve())
                return True
            except ValueError:
                continue
        return False
    
    def extract_text_from_pdf_ocr(self, file_path: str) -> str:
        """Извлечь текст из PDF через OCR (Tesseract)."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image
            
            print(f"[OCR] Processing: {file_path}")
            
            # Конвертить PDF в изображения (первые 5 страниц)
            images = convert_from_path(file_path, first_page=1, last_page=5, dpi=200)
            
            text = ""
            for page_num, image in enumerate(images):
                print(f"[OCR] Processing page {page_num + 1}/{len(images)}")
                # Запустить OCR на изображении
                page_text = pytesseract.image_to_string(image, lang='rus+eng')
                text += f"\n--- Page {page_num + 1} (OCR) ---\n"
                text += page_text
            
            return text if text.strip() else "[OCR: No text detected]"
        except ImportError as e:
            return f"[OCR libraries not installed: {e}]"
        except Exception as e:
            return f"[OCR error: {e}]"
    
    def read_file(self, file_path: str, use_ocr: bool = False) -> str:
        """Прочитать файл с проверкой безопасности."""
        if not self.is_safe_path(file_path):
            return None
        
        try:
            suffix = Path(file_path).suffix.lower()
            
            # PDF
            if suffix == ".pdf":
                if use_ocr:
                    print("[OCR] Using OCR mode")
                    return self.extract_text_from_pdf_ocr(file_path)
                else:
                    # Сначала попытаться простое извлечение
                    try:
                        import pypdf
                        with open(file_path, 'rb') as f:
                            pdf = pypdf.PdfReader(f)
                            text = ""
                            for page_num, page in enumerate(pdf.pages[:5]):
                                text += f"\n--- Page {page_num + 1} ---\n"
                                text += page.extract_text() or ""
                            
                            if text.strip() and len(text) > 100:
                                return text
                            else:
                                # Если текста мало — использовать OCR
                                print("[PDF] Text extraction unsuccessful, falling back to OCR")
                                return self.extract_text_from_pdf_ocr(file_path)
                    except Exception as e:
                        print(f"[PDF] Extraction failed: {e}, trying OCR")
                        return self.extract_text_from_pdf_ocr(file_path)
            
            # Текстовые форматы
            elif suffix in [".txt", ".md", ".json", ".yaml", ".csv", ".py", ".sh", ".log", ".html", ".xml"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    return content[:5000] + "\n... [truncated]" if len(content) > 5000 else content
            
            else:
                return None
        except Exception as e:
            return f"[Error: {e}]"
    
    def analyze_with_local_model(self, file_path: str, model: str = "qwen2.5:3b", 
                                  task: str = "анализ", use_ocr: bool = False) -> Dict:
        """Анализировать файл локальной моделью Ollama."""
        if not self.is_safe_path(file_path):
            return {"error": "Access denied"}
        
        # Читаем файл
        content = self.read_file(file_path, use_ocr=use_ocr)
        if not content or content.startswith("[Error") or content.startswith("[OCR"):
            return {"error": content or "Failed to read file"}
        
        # Обрезаем контент если слишком большой (3000 символов для быстроты)
        if len(content) > 3000:
            content = content[:3000] + "\n... [truncated]"
        
        # Создаем промпт с анализом файла
        file_name = Path(file_path).name
        prompt = f"""Analyze the following document ({file_name}) - {task}:

```
{content}
```

Provide a brief summary of key points and important information."""
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=300)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "file": file_path,
                    "model": model,
                    "analysis": data.get("response", "No response"),
                    "source": "ollama",
                    "ocr_used": use_ocr
                }
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    bridge = FileAccessBridgeWithOCR()
    
    if len(sys.argv) < 2:
        print("Usage: python file_access_bridge.py analyze <file_path> [model] [--ocr]")
        print("       python file_access_bridge.py read <file_path> [--ocr]")
        sys.exit(1)
    
    command = sys.argv[1]
    use_ocr = "--ocr" in sys.argv
    
    if command == "analyze":
        file_path = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "qwen2.5:3b"
        result = bridge.analyze_with_local_model(file_path, model, use_ocr=use_ocr)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "read":
        file_path = sys.argv[2]
        content = bridge.read_file(file_path, use_ocr=use_ocr)
        if content:
            print(content)
        else:
            print("Failed to read file")
    
    else:
        print(f"Unknown command: {command}")
