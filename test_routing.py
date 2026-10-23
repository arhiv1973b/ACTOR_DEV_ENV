from gemini_router import AliasRouter
import os

# Инициализация (используем фиктивные данные для теста)
router = AliasRouter(
    api_key="fake",
    manifest_path=os.path.expanduser("~/evidence_manifest.json"),
    alias_name="models/gemini-pro",
    fallback_models=[],
    timeout_sec=1
)

# Тест локального пути
print("--- Тест локального пути ---")
result_local = router.execute("Проанализируй статус дела.")
print(f"Результат: {result_local}")

# Тест удаленного пути (должен попытаться, но упасть из-за fake api key)
print("\n--- Тест удаленного пути ---")
try:
    result_remote = router.execute("Сложный аналитический отчет по кейсу.")
    print(f"Результат: {result_remote}")
except Exception as e:
    print(f"Ожидаемая ошибка (нет API ключа): {e}")
