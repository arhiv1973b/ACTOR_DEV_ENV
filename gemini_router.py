# gemini_router.py
import os
import json
import logging
import signal
import subprocess
from collections import defaultdict
from google import genai
from google.genai import errors

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Время ожидания ответа истекло")

class AliasRouter:
    def __init__(self, api_key, manifest_path, alias_name, fallback_models, timeout_sec=5):
        self.client = genai.Client(api_key=api_key)
        self.alias_name = alias_name
        self.fallback_models = fallback_models
        self.timeout_sec = timeout_sec
        self.available_models = []
        self.stats = defaultdict(lambda: {"success": 0, "errors": 0, "error_types": defaultdict(int)})
        self._load_manifest(manifest_path)

    def _load_manifest(self, manifest_path):
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            self.available_models = data.get("available_models", [])
            logging.info(f"Загружено {len(self.available_models)} моделей из манифеста.")
        except Exception as e:
            logging.error(f"Ошибка загрузки манифеста: {e}")
            self.available_models = []

    def classify_task(self, prompt):
        """Простейшая классификация задач"""
        local_keywords = ["статус", "лог", "интеграция", "проверка"]
        if any(keyword in prompt.lower() for keyword in local_keywords):
            return "LOCAL"
        return "REMOTE"

    def is_docker_available(self):
        try:
            subprocess.run(["docker", "info"], capture_output=True, timeout=2)
            return True
        except:
            return False

    def execute_local(self, prompt):
        """Выполнение задачи локально через Ollama"""
        logging.info(f"Выполнение локально: {prompt}")
        try:
            # Используем qwen2.5:7b, так как она у вас уже загружена
            cmd = ["docker", "exec", "-i", "actor_ollama", "ollama", "run", "qwen2.5:7b", prompt]
            # Добавляем timeout=30 секунд, чтобы скрипт не висел вечно
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return {"model": "local/qwen2.5:7b", "text": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            logging.error("Тайм-аут локального исполнения")
            return {"model": "local/qwen2.5:7b", "text": "Ошибка: превышено время ожидания локальной модели."}
        except Exception as e:
            logging.error(f"Ошибка локального исполнения: {e}")
            return {"model": "local/qwen2.5:7b", "text": f"Ошибка: {e}"}

    def execute(self, prompt):
        # Если Docker не отвечает, даже не пытаемся локально, сразу идем в облако
        if self.classify_task(prompt) == 'LOCAL' and self.is_docker_available():
            return self.execute_local(prompt)

        # Автоматическая перестановка приоритетов перед выполнением
        self._reorder_by_stability()

        candidates = [self.alias_name] + self.fallback_models
        for model_id in candidates:
            if model_id not in self.available_models:
                continue
            logging.info(f"Попытка выполнения на {model_id}")
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout_sec)

                response = self.client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                )

                signal.alarm(0)
                self.stats[model_id]["success"] += 1
                return {"model": model_id, "text": response.text}

            except TimeoutException:
                self.stats[model_id]["errors"] += 1
                self.stats[model_id]["error_types"]["timeout"] += 1
                logging.warning(f"Таймаут {model_id}. Переключение...")
                continue
            except errors.APIError as e:
                self.stats[model_id]["errors"] += 1
                self.stats[model_id]["error_types"]["api_error"] += 1
                logging.warning(f"API ошибка {model_id}: {e}. Переключение...")
                continue
            except errors.ServerError as e:
                self.stats[model_id]["errors"] += 1
                self.stats[model_id]["error_types"]["server_error"] += 1
                logging.warning(f"Серверная ошибка {model_id}: {e}. Переключение...")
                continue
            except Exception as e:
                self.stats[model_id]["errors"] += 1
                self.stats[model_id]["error_types"]["other"] += 1
                logging.warning(f"Ошибка {model_id}: {e}. Переключение...")
                continue

        raise RuntimeError(f"Все модели для алиаса {self.alias_name} недоступны.")

    def report_stats(self):
        """Возвращает статистику по всем моделям"""
        report = {}
        for model, data in self.stats.items():
            total = data["success"] + data["errors"]
            stability = (data["success"] / total * 100) if total > 0 else 0
            report[model] = {
                "success": data["success"],
                "errors": data["errors"],
                "stability_%": round(stability, 2),
                "error_types": dict(data["error_types"])
            }
        return report

    def _reorder_by_stability(self):
        """Переставляем fallback модели по стабильности (успехи/ошибки)"""
        def stability_score(model):
            data = self.stats[model]
            total = data["success"] + data["errors"]
            return (data["success"] / total) if total > 0 else 1.0  # новые модели считаем стабильными

        self.fallback_models.sort(key=lambda m: stability_score(m), reverse=True)
        logging.info(f"Перестановка приоритетов: {self.fallback_models}")

# Пример использования
if __name__ == "__main__":
    API_KEY = open(os.path.expanduser("~/.gemini_key")).read().strip()
    MANIFEST_PATH = os.path.expanduser("~/evidence_manifest.json")

    router = AliasRouter(
        api_key=API_KEY,
        manifest_path=MANIFEST_PATH,
        alias_name="models/gemini-3.5-pro",   # фиксированное имя для приложения
        fallback_models=[
            "models/gemini-3.1-pro-preview",
            "models/gemini-pro-latest",
            "models/gemini-2.5-pro",
            "models/gemini-flash-latest"
        ],
        timeout_sec=5
    )

    try:
        result = router.execute("Проведи анализ целостности данных.")
        print(f"[{result['model']}] {result['text']}")
    except Exception as e:
        print(f"Критический сбой: {e}")

    print("=== Статистика моделей ===")
    print(json.dumps(router.report_stats(), indent=2, ensure_ascii=False))
