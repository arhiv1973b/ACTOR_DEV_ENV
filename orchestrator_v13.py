# orchestrator_v13.py – A©t0r CORE ORCHESTRATOR v13
# Универсальные веса (Universal Weights) – локальный MCP‑сервер.
# Этот скрипт создаёт TCP‑сервер (AF_INET) на localhost:5000 и принимает
# JSON‑сообщения от клиентов (OCR, Whisper и др.).
# Сервер хранит в памяти словарь "весов" (dictionary) – простую структуру
# mapping: semantic_key -> vector_placeholder (будет заполнено позже).

import socket
import json
import threading
import pathlib
import sys

CONFIG_PATH = pathlib.Path(r"H:/ACTOR_DEV_ENV/agent.json")

def load_agent_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Ошибка] Не удалось загрузить config: {e}")
        return {}

# Глобальное хранилище весов (в дальнейшем будет заменено на векторную БД)
WEIGHTS = {}

def handle_client(conn, addr):
    with conn:
        data = conn.recv(4096)
        if not data:
            return
        try:
            request = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            conn.sendall(b"{\"error\": \"invalid json\"}")
            return
        # Пример команды: {"action": "store", "key": "example", "vector": [0.1, 0.2]}
        action = request.get("action")
        if action == "store":
            key = request.get("key")
            vector = request.get("vector")
            if key and vector:
                WEIGHTS[key] = vector
                response = {"status": "ok", "msg": f"stored {key}"}
            else:
                response = {"error": "missing key or vector"}
        elif action == "get":
            key = request.get("key")
            vector = WEIGHTS.get(key)
            response = {"status": "ok", "key": key, "vector": vector}
        else:
            response = {"error": f"unknown action {action}"}
        conn.sendall(json.dumps(response).encode("utf-8"))

def start_server(host="127.0.0.1", port=5000):
    print(f"[MCP] Запуск локального сервера на {host}:{port}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    cfg = load_agent_config()
    # Run legal risk auditor at startup
    import subprocess, os
    auditor_path = r"C:\Users\arhiv\.gemini\antigravity-cli\brain\25ad8a3d-2892-4aab-bf16-75a9d516708a\conflict_risk_analyzer.py"
    if os.path.exists(auditor_path):
        result = subprocess.run([sys.executable, auditor_path], cwd=os.path.dirname(__file__))
        if result.returncode != 0:
            print("[WARN] Conflict risk analysis failed.")
    else:
        print(f"[ERROR] Auditor not found at {auditor_path}")
    # При необходимости можно использовать параметры из cfg['model_config'] etc.
    start_server()
