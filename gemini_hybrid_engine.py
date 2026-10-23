#!/usr/bin/env python3
"""
Gemini API Integration Wrapper
Гибридный движок: Gemini API + локальные модели (Ollama) + кэширование
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
import subprocess
import sys

class GeminiHybridEngine:
    """Гибридный движок с поддержкой Gemini API и локальных моделей."""
    
    def __init__(self, gemini_api_key: str = None, local_model: str = "gemma:2b"):
        """
        Args:
            gemini_api_key: API ключ от Google Gemini (если None, используется GEMINI_API_KEY)
            local_model: Локальная модель Ollama для fallback
        """
        self.local_model = local_model
        self.cache_dir = Path("./cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Инициализация Gemini
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.gemini_available = True
            print("[GEMINI] API ключ установлен")
        else:
            self.gemini_available = False
            print("[GEMINI] API ключ не найден. Используется только локальная модель.")
    
    def get_cache_key(self, content: str) -> str:
        """Генерировать ключ кэша для контента."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def load_from_cache(self, cache_key: str) -> dict:
        """Загрузить результат из кэша."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_to_cache(self, cache_key: str, result: dict):
        """Сохранить результат в кэш."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def analyze_with_gemini(self, text: str, prompt: str = None) -> dict:
        """Анализировать текст с помощью Gemini API."""
        if not self.gemini_available:
            return None
        
        try:
            model = genai.GenerativeModel("gemini-pro")
            
            if prompt is None:
                prompt = """Проанализируй следующий документ и предоставь:
1. Краткое резюме (3-5 предложений)
2. Ключевые моменты (список)
3. Тип документа
4. Основные темы

Текст документа:
"""
            
            full_prompt = prompt + "\n\n" + text[:4000]  # Ограничение по размеру
            
            print("[GEMINI] Отправка запроса к API...")
            response = model.generate_content(full_prompt)
            
            return {
                "source": "gemini",
                "analysis": response.text,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
        except Exception as e:
            print(f"[GEMINI] Ошибка: {e}")
            return None
    
    def analyze_with_ollama(self, text: str, prompt: str = None) -> dict:
        """Анализировать текст с помощью локальной модели Ollama."""
        try:
            if prompt is None:
                prompt = "Кратко проанализируй этот текст (максимум 3 предложения):\n\n"
            
            full_prompt = prompt + text[:2000]
            
            print(f"[OLLAMA] Использование модели: {self.local_model}")
            
            result = subprocess.run(
                ["ollama", "run", self.local_model, full_prompt],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "source": "ollama",
                    "analysis": result.stdout,
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                }
            else:
                print(f"[OLLAMA] Ошибка: {result.stderr}")
                return None
        except Exception as e:
            print(f"[OLLAMA] Ошибка: {e}")
            return None
    
    def analyze(self, text: str, prompt: str = None, use_gemini_first: bool = True) -> dict:
        """
        Гибридный анализ: сначала Gemini, затем Ollama если ошибка.
        
        Args:
            text: Текст для анализа
            prompt: Кастомный промпт (опционально)
            use_gemini_first: Использовать ли сначала Gemini (если доступен)
        
        Returns:
            dict с результатом анализа
        """
        cache_key = self.get_cache_key(text)
        
        # Проверить кэш
        cached = self.load_from_cache(cache_key)
        if cached:
            print("[CACHE] Результат найден в кэше")
            return cached
        
        result = None
        
        # Попытка 1: Gemini
        if use_gemini_first and self.gemini_available:
            print("[HYBRID] Попытка 1: Gemini API...")
            result = self.analyze_with_gemini(text, prompt)
        
        # Попытка 2: Ollama (fallback или если Gemini недоступен)
        if result is None:
            print("[HYBRID] Попытка 2: Ollama (локальная модель)...")
            result = self.analyze_with_ollama(text, prompt)
        
        # Сохранить в кэш
        if result:
            self.save_to_cache(cache_key, result)
        
        return result or {"status": "failed", "error": "Оба источника недоступны"}

if __name__ == "__main__":
    # Пример использования
    engine = GeminiHybridEngine()
    
    test_text = """
    Это судебное решение от 2019 года касается дела о res judicata.
    Суд признал, что вопрос был рассмотрен ранее и не может быть пересмотрен.
    """
    
    result = engine.analyze(test_text)
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ:")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))
