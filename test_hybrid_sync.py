# test_hybrid_sync.py
import os
import json
import logging
from gemini_router import AliasRouter

# Настройка логирования для теста
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_test():
    # Пути (учитывая текущую директорию)
    API_KEY = os.environ.get("SECRET_VAR")
    MANIFEST_PATH = "evidence_manifest.json"
    CONFIG_PATH = "actor_config.yaml"

    print("=== ЗАПУСК ТЕСТА СИНХРОНИЗАЦИИ ВЕСОВ (HYBRID MODE) ===")
    
    # Инициализация роутера
    router = AliasRouter(
        api_key=API_KEY,
        manifest_path=MANIFEST_PATH,
        config_path=CONFIG_PATH,
        alias_name="models/gemini-3.5-pro",
        fallback_models=[
            "models/gemini-3.1-pro-preview",
            "models/gemini-pro-latest"
        ],
        timeout_sec=10
    )

    prompt = "Проанализируй целостность системы и выяви возможные точки отказа в цепочке калибровки."

    try:
        print(f"Отправка промпта: {prompt}")
        result = router.execute(prompt)
        
        print("\n--- РЕЗУЛЬТАТ ТЕСТА ---")
        print(f"Модель: {result.get('model')}")
        print(f"Текст: {result.get('text')}")
        if result.get('calibrated'):
            print("✅ СТАТУС: Калибровка весов прошла успешно!")
        else:
            print("❌ СТАТУС: Калибровка НЕ была применена.")
            
    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")

if __name__ == "__main__":
    run_test()
