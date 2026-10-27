#!/usr/bin/env python3
"""
Unified Model Integration Layer
Единый интерфейс для локальных и облачных моделей
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import subprocess

class UnifiedModelInterface:
    """Единый интерфейс для всех моделей (локальные + облачные)."""
    
    def __init__(self):
        self.cache_dir = Path("./model_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.models = self._load_available_models()
    
    def _load_available_models(self) -> Dict[str, Dict]:
        """Загрузить список доступных моделей."""
        return {
            # Локальные модели (Ollama)
            "ollama": {
                "gemma:2b": {"type": "local", "provider": "ollama", "speed": "fast", "quality": "medium"},
                "qwen2.5:3b": {"type": "local", "provider": "ollama", "speed": "fast", "quality": "medium"},
                "qwen2.5:7b": {"type": "local", "provider": "ollama", "speed": "medium", "quality": "high"},
                "llama3.1:8b": {"type": "local", "provider": "ollama", "speed": "medium", "quality": "high"},
                "llama3.2:latest": {"type": "local", "provider": "ollama", "speed": "medium", "quality": "high"},
                "deepseek-coder:1.3b": {"type": "local", "provider": "ollama", "speed": "fast", "quality": "medium"},
            },
            # Облачные модели
            "gemini": {
                "gemini-pro": {"type": "cloud", "provider": "google", "api_key_env": "GEMINI_API_KEY"},
                "gemini-pro-vision": {"type": "cloud", "provider": "google", "api_key_env": "GEMINI_API_KEY"},
            },
            "openai": {
                "gpt-4": {"type": "cloud", "provider": "openai", "api_key_env": "OPENAI_API_KEY"},
                "gpt-3.5-turbo": {"type": "cloud", "provider": "openai", "api_key_env": "OPENAI_API_KEY"},
            },
            "anthropic": {
                "claude-3-opus": {"type": "cloud", "provider": "anthropic", "api_key_env": "ANTHROPIC_API_KEY"},
                "claude-3-sonnet": {"type": "cloud", "provider": "anthropic", "api_key_env": "ANTHROPIC_API_KEY"},
            }
        }
    
    def list_available_models(self) -> Dict:
        """Вывести все доступные модели."""
        print("\n" + "="*70)
        print("ДОСТУПНЫЕ МОДЕЛИ")
        print("="*70)
        
        for provider, models in self.models.items():
            print(f"\n[{provider.upper()}]")
            for model_name, config in models.items():
                model_type = config.get("type", "unknown")
                status = "✅" if self._check_model_availability(provider, model_name) else "⏳"
                print(f"  {status} {model_name:<30} ({config.get('speed', 'unknown')})")
        
        return self.models
    
    def _check_model_availability(self, provider: str, model_name: str) -> bool:
        """Проверить, доступна ли модель."""
        if provider == "ollama":
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return model_name.lower() in result.stdout.lower()
            except:
                return False
        else:
            # Облачные модели проверяются наличием API ключа
            config = self.models.get(provider, {}).get(model_name, {})
            api_key_env = config.get("api_key_env")
            return bool(os.getenv(api_key_env)) if api_key_env else False
    
    def query_local_model(self, model: str, prompt: str, stream: bool = False) -> str:
        """Запрос к локальной модели (Ollama)."""
        print(f"[LOCAL] Запрос к модели: {model}")
        
        try:
            cmd = ["ollama", "run", model, prompt]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Model request timeout (180s)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def query_cloud_model(self, provider: str, model: str, prompt: str) -> str:
        """Запрос к облачной модели."""
        print(f"[CLOUD] Запрос к {provider}/{model}")
        
        config = self.models.get(provider, {}).get(model, {})
        api_key_env = config.get("api_key_env")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            return f"Error: API ключ {api_key_env} не установлен"
        
        # Интеграция с конкретными провайдерами
        if provider == "gemini":
            return self._query_gemini(model, prompt, api_key)
        elif provider == "openai":
            return self._query_openai(model, prompt, api_key)
        elif provider == "anthropic":
            return self._query_anthropic(model, prompt, api_key)
        else:
            return f"Error: Unknown provider {provider}"
    
    def _query_gemini(self, model: str, prompt: str, api_key: str) -> str:
        """Запрос к Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            llm = genai.GenerativeModel(model)
            response = llm.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _query_openai(self, model: str, prompt: str, api_key: str) -> str:
        """Запрос к OpenAI API."""
        try:
            import openai
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _query_anthropic(self, model: str, prompt: str, api_key: str) -> str:
        """Запрос к Claude API (Anthropic)."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def query(self, model: str, prompt: str, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Универсальный запрос к любой модели.
        
        Args:
            model: Имя модели
            prompt: Промпт
            provider: Провайдер (если None, определяется автоматически)
        
        Returns:
            dict с результатом
        """
        # Определить провайдера если не указан
        if provider is None:
            for prov, models in self.models.items():
                if model in models:
                    provider = prov
                    break
        
        if not provider:
            return {
                "status": "error",
                "error": f"Model {model} not found"
            }
        
        model_config = self.models.get(provider, {}).get(model, {})
        model_type = model_config.get("type", "unknown")
        
        print(f"\n{'='*60}")
        print(f"Model: {model}")
        print(f"Provider: {provider} ({model_type})")
        print(f"{'='*60}\n")
        
        try:
            if model_type == "local":
                response = self.query_local_model(model, prompt)
            elif model_type == "cloud":
                response = self.query_cloud_model(provider, model, prompt)
            else:
                response = "Unknown model type"
            
            result = {
                "status": "success",
                "model": model,
                "provider": provider,
                "type": model_type,
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Сохранить в кэш
            self._save_to_cache(result)
            
            return result
        
        except Exception as e:
            return {
                "status": "error",
                "model": model,
                "provider": provider,
                "error": str(e)
            }
    
    def _save_to_cache(self, result: Dict):
        """Сохранить результат в кэш."""
        cache_file = self.cache_dir / f"{result['model']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    interface = UnifiedModelInterface()
    
    # Показать доступные модели
    interface.list_available_models()
    
    # Пример запроса к локальной модели
    print("\n" + "="*60)
    print("ПРИМЕР ЗАПРОСА К ЛОКАЛЬНОЙ МОДЕЛИ")
    print("="*60)
    
    result = interface.query(
        model="gemma:2b",
        prompt="Кратко объясни что такое Machine Learning"
    )
    
    print("\nРЕЗУЛЬТАТ:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
