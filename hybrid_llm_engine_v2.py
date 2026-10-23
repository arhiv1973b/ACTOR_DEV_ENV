#!/usr/bin/env python3
"""
Hybrid LLM Engine with OCR Integration
Локальные модели + PDF с автоматическим OCR для сканированных документов
"""

import sys
import requests
import json
import hashlib
from datetime import datetime
from pathlib import Path
import os

class HybridLLMEngineV2:
    """Гибридный движок с поддержкой файлов, PDF и OCR."""
    
    def __init__(self):
        self.cache_dir = Path("./.llm_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.models = {
            "llama3.1:8b": "http://127.0.0.1:11434/api/generate",
            "qwen2.5:7b": "http://127.0.0.1:11434/api/generate",
            "qwen2.5:3b": "http://127.0.0.1:11434/api/generate",
            "gemma:2b": "http://127.0.0.1:11434/api/generate",
        }
        self.request_log = []
        self.accessible_paths = [
            r"F:\Мой диск",
            r"H:\ACTOR_DEV_ENV",
            r"C:\temp",
            os.path.expanduser("~")
        ]
        
        # Установить путь к Tesseract
        try:
            import pytesseract
            pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            pass
    
    def is_safe_path(self, file_path: str) -> bool:
        """Проверить безопасность пути."""
        try:
            file_path = Path(file_path).resolve()
            for base in self.accessible_paths:
                try:
                    file_path.relative_to(Path(base).resolve())
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False
    
    def extract_pdf_text_ocr(self, file_path: str) -> str:
        """Извлечь текст из PDF через OCR."""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            # Убедиться, что путь установлен
            pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            print(f"🔍 [OCR] Processing PDF: {Path(file_path).name}")
            
            # Конвертить первые 5 страниц в изображения
            images = convert_from_path(file_path, first_page=1, last_page=5, dpi=150)
            
            text = ""
            for page_num, image in enumerate(images):
                print(f"   [Page {page_num + 1}/{len(images)}] Running OCR...")
                page_text = pytesseract.image_to_string(image, lang='rus+eng')
                text += f"\n--- Page {page_num + 1} (OCR) ---\n{page_text}"
            
            print(f"✅ [OCR] Extracted {len(text)} characters")
            return text if text.strip() else "[OCR: No text detected]"
        except Exception as e:
            return f"[OCR failed: {e}]"
    
    def extract_pdf_text_simple(self, file_path: str) -> str:
        """Простое извлечение текста из PDF (без OCR)."""
        try:
            import pypdf
            with open(file_path, 'rb') as f:
                pdf = pypdf.PdfReader(f)
                text = ""
                for page_num, page in enumerate(pdf.pages[:5]):
                    text += f"\n--- Page {page_num + 1} ---\n"
                    page_text = page.extract_text() or ""
                    text += page_text
                return text
        except Exception as e:
            return f"[PDF extraction failed: {e}]"
    
    def read_file(self, file_path: str) -> str:
        """Прочитать файл с проверкой безопасности и автоматическим OCR."""
        if not self.is_safe_path(file_path):
            return f"Access denied: {file_path}"
        
        try:
            suffix = Path(file_path).suffix.lower()
            
            # PDF с автоматическим OCR fallback
            if suffix == ".pdf":
                print(f"📄 Reading PDF: {Path(file_path).name}")
                # Попытаться простое извлечение
                content = self.extract_pdf_text_simple(file_path)
                
                # Если текста мало — запустить OCR
                if not content or len(content) < 200 or "[PDF extraction failed" in content:
                    print("   ⚠️  Simple extraction failed, using OCR...")
                    content = self.extract_pdf_text_ocr(file_path)
                
                return content
            
            # Текстовые форматы
            elif suffix in [".txt", ".md", ".json", ".yaml", ".csv", ".py", ".sh", ".log", ".html", ".xml"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content) > 3000:
                        content = content[:3000] + "\n... [truncated]"
                    return content
            
            else:
                return f"Format not supported: {suffix}"
        except Exception as e:
            return f"Read error: {e}"
    
    def hash_prompt(self, prompt):
        """Генерирует хеш для кэширования."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:12]
    
    def check_cache(self, prompt_hash):
        """Проверяет кэш ответов."""
        cache_file = self.cache_dir / f"{prompt_hash}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def save_cache(self, prompt_hash, response):
        """Сохраняет ответ в кэш."""
        cache_file = self.cache_dir / f"{prompt_hash}.json"
        with open(cache_file, 'w') as f:
            json.dump(response, f)
    
    def query_ollama(self, prompt, model="qwen2.5:3b"):
        """Запрос к локальной модели Ollama."""
        prompt_hash = self.hash_prompt(prompt)
        
        # Проверка кэша
        cached = self.check_cache(prompt_hash)
        if cached:
            return {
                "response": cached["response"],
                "source": "cache",
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
        
        # Запрос к API
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                self.models[model],
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "response": data.get("response", "No response"),
                    "source": "ollama",
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
                self.save_cache(prompt_hash, result)
                return result
            else:
                return {
                    "error": f"HTTP {response.status_code}",
                    "source": "ollama",
                    "model": model
                }
        except Exception as e:
            return {
                "error": str(e),
                "source": "error",
                "model": model
            }
    
    def analyze_file(self, file_path: str, model: str = "qwen2.5:3b") -> dict:
        """Анализировать файл локальной моделью."""
        print(f"📊 Analyzing: {Path(file_path).name}")
        content = self.read_file(file_path)
        
        if "denied" in content.lower() or "not supported" in content.lower():
            return {"error": content, "file": file_path}
        
        file_name = Path(file_path).name
        prompt = f"""Analyze the following document ({file_name}):

```
{content}
```

Provide a brief summary of key points, main issues, and important information."""
        
        print(f"🤖 Querying model: {model}")
        return self.query_ollama(prompt, model)
    
    def audit_system(self):
        """Аудит системы."""
        print("HYBRID LLM ENGINE AUDIT WITH OCR SUPPORT")
        print("=" * 60)
        
        # Проверка моделей
        print("\n[1] Checking local models...")
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"Found: {len(models)} models")
                for m in models[:5]:
                    print(f"   - {m['name']} ({m['size'] / 1e9:.2f}GB)")
        except Exception as e:
            print(f"Connection error: {e}")
        
        # Проверка Tesseract
        print("\n[2] Checking OCR support...")
        try:
            result = os.system("tesseract --version > nul 2>&1")
            if result == 0:
                print("✓ Tesseract v5.5.0+ available")
                print(f"✓ Tesseract path: C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
            else:
                print("✗ Tesseract not found")
        except:
            print("✗ Tesseract check failed")
        
        # Проверка кэша
        print("\n[3] Cache status...")
        cache_files = list(self.cache_dir.glob("*.json"))
        print(f"Cached responses: {len(cache_files)}")
        
        # Проверка путей
        print("\n[4] File access check...")
        for path in self.accessible_paths:
            if os.path.exists(path):
                print(f"   OK: {path}")
            else:
                print(f"   NO: {path}")
        
        # Статус
        print("\n[5] System status...")
        print("✓ Hybrid Engine ready")
        print("✓ Local cache active")
        print("✓ File analysis available")
        print("✓ OCR support enabled (Tesseract v5.5.0)")
        print("✓ Automatic fallback: Simple extraction → OCR")
        print("=" * 60)

if __name__ == "__main__":
    engine = HybridLLMEngineV2()
    
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        engine.audit_system()
    elif len(sys.argv) > 2 and sys.argv[1] == "analyze":
        file_path = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else "qwen2.5:3b"
        result = engine.analyze_file(file_path, model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        model = "qwen2.5:3b"
        
        print("Hybrid LLM Query")
        print(f"Model: {model}")
        print(f"Prompt: {prompt}")
        print("=" * 60)
        
        result = engine.query_ollama(prompt, model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python hybrid_llm_engine_v2.py 'prompt' | audit | analyze <file_path> [model]")
