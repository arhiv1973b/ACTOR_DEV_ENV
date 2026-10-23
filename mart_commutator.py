import os
import time
import logging
from google import genai
from google.genai import errors
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SmartCommutator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # Группируем модели, чтобы не спамить всё подряд
        self.model_pool = ["models/gemini-2.0-flash", "models/gemini-2.5-flash", "models/gemini-flash-latest"]

    # Рекурсивная логика ожидания (Backoff): если 429, ждем дольше
    @retry(wait=wait_exponential(multiplier=1, min=4, max=60), 
           stop=stop_after_attempt(5),
           retry=retry_if_exception_type(errors.APIError))
    def _call_model(self, model_id, prompt):
        return self.client.models.generate_content(model=model_id, contents=prompt)

    def execute(self, prompt):
        for model_id in self.model_pool:
            logging.info(f"Запрос к {model_id}...")
            try:
                response = self._call_model(model_id, prompt)
                return response.text
            except Exception as e:
                logging.warning(f"{model_id} не ответил, перехожу к следующему.")
                continue
        raise RuntimeError("Все модели исчерпали квоты.")

# Инициализация ключа
key = os.getenv("GEMINI_API_KEY") or open(os.path.expanduser("~/.gemini_key")).read().strip()
comm = SmartCommutator(key)
print(comm.execute("Проверка связи."))