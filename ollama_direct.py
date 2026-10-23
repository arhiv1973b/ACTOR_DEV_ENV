#!/usr/bin/env python3
"""
Local Ollama Direct Access - No Cloud API
Работает только с локальными моделями через HTTP API
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
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "No response")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ollama_direct.py 'prompt' [model]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "llama3:latest"
    
    print(f"🤖 Ollama Query")
    print(f"Model: {model}")
    print(f"Prompt: {prompt}")
    print("=" * 60)
    
    result = query_ollama(prompt, model)
    print(result)

if __name__ == "__main__":
    main()
