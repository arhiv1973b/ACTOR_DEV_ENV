import os
import google.generativeai as genai

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("[!] ERROR: GEMINI_API_KEY не найдена в окружении.")
    exit(1)

genai.configure(api_key=key)
# Используем самую актуальную модель
model = genai.GenerativeModel('gemini-2.0-flash-exp')
try:
    response = model.generate_content("Ping")
    print(f"[A©t0r] OK: API-ключ валиден. Модель: gemini-2.0-flash-exp")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"[!] Ошибка подключения: {e}")
