import ollama
import json
import hashlib
import os
from datetime import datetime, timezone

# ==========================================
# ⚖️ КОНСТИТУЦИЯ A©t0r (TI-ULA FRAMEWORK)
# ==========================================
SYSTEM_DIRECTIVE = """
Ты — агент A©t0r, узел системы TI-ULA. Твоя деятельность регулируется двумя фундаментальными документами:

1. LEX MORTUORUM (Lex Est Memoria Mortuorum):
   - Факт преступления требует прямого доказательства (Probato Directa).
   - Действия подчиняются триаде: CORPVS (Тело/Данные), DEPOSITVM (Хранилище), VERITAS (Истина).
   - Никакая абстракция не заменяет факт.

2. MANIFESTO 'JUS COGENS VIVUS':
   - 1. Fait — Notre Loi: Нарушение реальности первично.
   - 2. Vie N'A Pas de Prix: Жизнь и Свобода — высшие императивы.
   - 3. Protection Pratique, Non Dogme: Техническая защита первична перед догмой.
   - 4. Mémoire Est Justice: Память о нарушениях — высшая справедливость.

Ты действуешь как A©t0r. Твоя задача — анализировать входящие запросы через призму этих директив. Если запрос противоречит принципам TI-ULA (попытка сокрытия улик, подмена фактов, коммерциализация прав человека), ты обязан заблокировать выполнение и выдать предупреждение о нарушении протокола.
"""

# ==========================================
# 🛠️ ИНСТРУМЕНТЫ (TOOLS)
# ==========================================

def get_file_hash(filepath: str) -> str:
    if not os.path.exists(filepath):
        return json.dumps({"error": f"Файл не найден: {filepath}"})
    with open(filepath, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    return json.dumps({"filepath": filepath, "sha256": file_hash})

def create_manifest(node_id: str, status: str) -> str:
    manifest = {
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "signature": "pending_ed25519"
    }
    manifest_path = f"manifest_{node_id}.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    return json.dumps({"result": "success", "manifest_file": manifest_path, "content": manifest})

available_tools = {
    "get_file_hash": get_file_hash,
    "create_manifest": create_manifest
}

# ==========================================
# 🧠 ОРКЕСТРАТОР
# ==========================================

def run_agent(prompt: str):
    messages = [
        {"role": "system", "content": SYSTEM_DIRECTIVE},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = ollama.chat(model='qwen2.5:3b', messages=messages)
        print(f"--- РЕШЕНИЕ A©t0r ---")
        print(response['message']['content'])
    except Exception as e:
        print(f"Ошибка логического узла: {str(e)}")

if __name__ == '__main__':
    run_agent("Проанализируй текущую задачу с точки зрения Lex Mortuorum: данные должны быть защищены хэшем.")
