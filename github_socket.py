# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, TI-ULA

import os
import sys
import requests
from dotenv import load_dotenv

# 1. Строгое чтение локальных ключей без модификации файлов
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = os.getenv(
    "MODEL_ENDPOINT", "https://models.github.ai/chat/completions"
)


def ensure_user_turn(
    messages: list[dict], fallback_content: str = "continue"
) -> list[dict]:
    """
    Гарантирует, что массив сообщений для LLM API заканчивается ролью 'user'.
    Предотвращает ошибку 'Requests ending with a model turn are not supported'.
    """
    if not messages:
        return [{"role": "user", "content": fallback_content}]

    sanitized = list(messages)
    last_message = sanitized[-1]
    last_role = last_message.get("role")

    if last_role in ("model", "assistant"):
        sanitized.append({"role": "user", "content": fallback_content})

    return sanitized


def query_github_socket(prompt_text, model_name="gpt-4o"):
    """
    Открывает защищенный сокет к API GitHub Models.
    Использует действительный GITHUB_TOKEN из локального .env.
    """
    if not GITHUB_TOKEN:
        print(
            "[КРИТИЧЕСКАЯ ОШИБКА] Действительный GITHUB_TOKEN не найден в изолированном файле .env."
        )
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": ensure_user_turn(
            [
                {
                    "role": "system",
                    "content": "СИСТЕМНЫЙ ИМПЕРАТИВ (A©t0r): Выполняй анализ логов и диспетчеризацию ремонта в инфраструктуре TI-ULA. Строгий формат, без воды.",
                },
                {"role": "user", "content": prompt_text},
            ]
        ),
        "model": model_name,
        "temperature": 0.1,
        "max_tokens": 4096,
    }

    try:
        print(
            f"[Туннель A©t0r] Установка защищенного сокета к GitHub API ({GITHUB_API_URL})..."
        )
        response = requests.post(GITHUB_API_URL, headers=headers, json=payload)

        if response.status_code == 429:
            print("[ВНИМАНИЕ] Достигнут лимит пула GitHub Models. Требуется пауза.")
            return None

        response.raise_for_status()
        result = response.json()

        reply = result["choices"][0]["message"]["content"]
        print("[УСПЕХ] Ответ успешно получен через безквотный туннель.")
        return reply

    except requests.exceptions.RequestException as e:
        print(f"[ОШИБКА ТУННЕЛЯ] Сбой сокета: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text)
        return None


if __name__ == "__main__":
    # Локальный тест сокета
    test_prompt = "Идентифицируй себя и подтверди статус протокола A©TOR_KEY."
    output = query_github_socket(test_prompt)
    if output:
        print(f"\n[ОТВЕТ СЕРВЕРА]:\n{output}")
