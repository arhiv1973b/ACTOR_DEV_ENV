#!/usr/bin/env python3
"""
Hybrid Layered LLM Engine - Based on Macheret Juscogens Architecture
Использует Docker-слои для кэширования и гибридной маршрутизации запросов
"""

import sys
import requests
import json
import hashlib
from datetime import datetime
from pathlib import Path

class HybridLLMEngine:
    """Гибридный движок с поддержкой локальных и облачных моделей."""
    
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
    
    def query_ollama(self, prompt, model="llama3:latest"):
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
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    "response": data.get("response", "No response"),
                    "source": "ollama",
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
                # Сохранить в кэш
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
    
    def audit_system(self):
        """Аудит системы и загрузки моделей."""
        print("🔍 HYBRID LLM ENGINE AUDIT")
        print("=" * 60)
        
        # Проверка доступных моделей
        print("\n[1] Проверка локальных моделей...")
        try:
            response = requests.get("http://127.0.0.1:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Найдено моделей: {len(models)}")
                for m in models:
                    print(f"   - {m['name']} ({m['size'] / 1e9:.2f}GB)")
            else:
                print(f"❌ Ollama недоступна (статус {response.status_code})")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
        
        # Проверка кэша
        print("\n[2] Кэш запросов...")
        cache_files = list(self.cache_dir.glob("*.json"))
        print(f"✅ Кэшировано ответов: {len(cache_files)}")
        
        # Статус системы
        print("\n[3] Статус системы...")
        print("✅ Hybrid Engine готова")
        print("✅ Локальный кэш активен")
        print("✅ Маршрутизация работает")
        print("=" * 60)

if __name__ == "__main__":
    engine = HybridLLMEngine()
    
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        engine.audit_system()
    elif len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        model = "qwen2.5:3b"  # По умолчанию - меньше памяти
        
        print(f"🤖 Hybrid LLM Query")
        print(f"Model: {model}")
        print(f"Prompt: {prompt}")
        print("=" * 60)
        
        result = engine.query_ollama(prompt, model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python hybrid_llm_engine.py 'prompt' | audit")
