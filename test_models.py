import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Ошибка: Переменная окружения GEMINI_API_KEY не найдена!")
    exit(1)

client = genai.Client(api_key=api_key)

print("=== Проверка доступных моделей API ===")
try:
    for model in client.models.list():
        print(f"Имя: {getattr(model, 'name', 'N/A')}")
        print(f"Отображаемое имя: {getattr(model, 'display_name', 'N/A')}")
        if hasattr(model, '__dict__'):
            print(f"Доступные поля: {list(model.__dict__.keys())}")
        print("-" * 50)
except Exception as e:
    print(f"Произошла ошибка при запросе списка моделей: {e}")
