#!/usr/bin/env python3
"""
Local Ollama Only - No Gemini Cloud API
Работает только с локальными моделями
"""

import sys
import requests
import json

def query_ollama(prompt, model="llama3:latest"):
    """Запрос к локальному Ollama."""
    url = "http://127.0.0.1:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        print(f"🤖 Querying {model}...")
        response = requests.post(url, json=payload, timeout=180)
        data = response.json()
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        return data.get("response", "No response")
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ollama_only.py 'prompt' [model]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "llama3:latest"
    
    print("=" * 60)
    print(f"📝 Prompt: {prompt}")
    print(f"🤖 Model: {model}")
    print("=" * 60)
    
    result = query_ollama(prompt, model)
    print(result)
    print("=" * 60)
