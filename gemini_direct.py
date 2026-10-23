#!/usr/bin/env python3
"""
Gemini API Direct Access - Restored
Обход интерактивного режима, прямой вызов API
"""

import os
import sys
from google import genai

def restore_and_test():
    """Восстановить доступ к API и протестировать."""
    
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY не установлен")
        sys.exit(1)
    
    print("🔧 ВОССТАНОВЛЕНИЕ GEMINI API")
    print("=" * 60)
    
    # 1. Инициализация клиента
    print("\n[1/4] Инициализация клиента...")
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Клиент готов")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    
    # 2. Список доступных моделей
    print("\n[2/4] Проверка доступных моделей...")
    try:
        models = client.models.list()
        available = [m.name for m in models if 'gemini' in m.name.lower()]
        print(f"✅ Доступные модели: {len(available)}")
        for model in available[:5]:
            print(f"   - {model}")
    except Exception as e:
        print(f"⚠️  Ошибка при списке моделей: {e}")
    
    # 3. Тестовый запрос
    print("\n[3/4] Тестовый запрос к API...")
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents='Ответь одним словом: готова ли система?'
        )
        result = response.text
        print(f"✅ Ответ получен: {result}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        sys.exit(1)
    
    # 4. Статус
    print("\n[4/4] Финальный статус...")
    print("=" * 60)
    print("✅ API ВОССТАНОВЛЕН И РАБОТАЕТ")
    print("=" * 60)
    print("\nМодель готова к использованию.")
    print("\nДальнейшие запросы:")
    print("  python gemini_direct.py 'ваш запрос'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Пользовательский запрос
        prompt = ' '.join(sys.argv[1:])
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY не установлен")
            sys.exit(1)
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        print(response.text)
    else:
        # Восстановление и тест
        restore_and_test()
