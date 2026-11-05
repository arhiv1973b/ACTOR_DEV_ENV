# A©TOR_KEY="# [⚖ A©tor Declaration]"
# A©t0r Identity: arhiv1973b
# Legal Scope: Erga Omnes, TI-ULA

import os
import sys
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Эндпоинты для двухступенчатой авторизации Copilot
TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
COPILOT_API_URL = "https://api.githubcopilot.com/chat/completions"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"


def get_secure_token():
    token = os.getenv("GITHUB_TOKEN")
    if token and "your_actual" not in token:
        return token
    try:
        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )
        cli_token = result.stdout.strip()
        if cli_token:
            print("[ИНТЕГРАЦИЯ CLI] GITHUB_TOKEN успешно извлечен из gh CLI.")
            return cli_token
    except Exception:
        pass
    return None


def get_copilot_token(github_token):
    """Обмен стандартного PAT на временный сессионный токен Copilot"""
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/json",
        "Editor-Version": "vscode/1.85.0",
        "Editor-Plugin-Version": "copilot-chat/0.11.0",
        "User-Agent": "GitHubCopilotChat/0.11.0",
    }
    try:
        response = requests.get(TOKEN_URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("token")
    except requests.exceptions.RequestException as e:
        print(
            f"[ОШИБКА АВТОРИЗАЦИИ] Не удалось получить токен Copilot. Проверьте права ключа: {str(e)}"
        )
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text)
            if e.response.status_code == 401:
                print(
                    "[РЕКОМЕНДАЦИЯ] Выполните `gh auth refresh -s copilot` для добавления прав Copilot."
                )
        return None


def query_github_socket(prompt_text, model_name="gpt-4o"):
    github_token = get_secure_token()
    if not github_token:
        print("[КРИТИЧЕСКАЯ ОШИБКА] Доступ запрещен. GITHUB_TOKEN не найден.")
        # Fallback to Ollama if no github token
    else:
        print("[Авторизация] Получение сессионного ключа GitHub Copilot...")
        copilot_token = get_copilot_token(github_token)

        if copilot_token:
            # API Copilot требует заголовки редактора для подтверждения легитимности сокета
            headers = {
                "Authorization": f"Bearer {copilot_token}",
                "Content-Type": "application/json",
                "Editor-Version": "vscode/1.80.0",
                "Editor-Plugin-Version": "copilot-chat/0.1.0",
            }

            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "СИСТЕМНЫЙ ИМПЕРАТИВ (A©t0r): TI-ULA Infrastructure AI Tunnel. Отвечай кратко, строго по делу.",
                    },
                    {"role": "user", "content": prompt_text},
                ],
                "model": model_name,
                "temperature": 0.1,
                "max_tokens": 4096,
            }

            try:
                print(
                    f"[Туннель A©t0r] Установка защищенного сокета к Copilot API ({COPILOT_API_URL})..."
                )
                response = requests.post(
                    COPILOT_API_URL, headers=headers, json=payload, timeout=30
                )

                if response.status_code == 429:
                    print(
                        "[ВНИМАНИЕ] Лимит пула исчерпан. Переход на локальный резерв (Ollama)..."
                    )
                else:
                    try:
                        result = response.json()
                        if "choices" in result:
                            print("[УСПЕХ] Ответ успешно получен через Copilot API.")
                            return result["choices"][0]["message"]["content"]
                        else:
                            print(f"[ОШИБКА СТРУКТУРЫ] Неожиданный ответ API: {result}")
                    except ValueError:
                        print(
                            f"[СБОЙ ЭНДПОИНТА] Сервер вернул текст вместо JSON. Код: {response.status_code}"
                        )
                        print(f"RAW-ответ сервера: {response.text.strip()}")
            except requests.exceptions.RequestException as e:
                print(
                    f"[ОШИБКА ТУННЕЛЯ] Сбой запроса: {str(e)}. Переход на локальный резерв (Ollama)..."
                )

    # Fallback to Local Ollama via CLI subprocess
    print(
        f"[TI-ULA Fallback] Подключение к локальной модели Ollama через CLI ({OLLAMA_MODEL})..."
    )
    try:
        cmd = [
            "ollama",
            "run",
            OLLAMA_MODEL,
            f"Системный императив (A©t0r): TI-ULA Infrastructure AI Tunnel.\n\nЗапрос: {prompt_text}",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode == 0:
            reply = result.stdout.strip()
            print("[УСПЕХ] Ответ получен через локальный резервный узел Ollama (CLI).")
            return reply
        else:
            print(f"[ОШИБКА OLLAMA CLI] {result.stderr}")
            return None
    except Exception as local_err:
        print(
            f"[КРИТИЧЕСКАЯ ОШИБКА РЕЗЕРВА] Локальный узел Ollama недоступен: {str(local_err)}"
        )
        return None


if __name__ == "__main__":
    test_prompt = "Идентифицируй себя и подтверди статус соединения через API Copilot."
    output = query_github_socket(test_prompt)
    if output:
        print(f"\n[ОТВЕТ ТУННЕЛЯ]:\n{output}")
