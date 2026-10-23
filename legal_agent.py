import sqlite3
import json
import logging
import os
from google import genai
from google.genai.errors import ClientError
from pathlib import Path
from datetime import datetime, timezone

# ── КОНФИГУРАЦИЯ ────────────────────────────────────────────────────────
DB_PATH = Path(r"H:/ACTOR_DEV_ENV/legal_cases.db")
LOG_PATH = Path(r"H:/ACTOR_DEV_ENV/logs/legal_agent.log")

logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s - A©tor Legal - %(levelname)s - %(message)s')
logger = logging.getLogger("LegalAgent")

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def add_statute(title, text, source):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO statutes (title, text, source, created_at) VALUES (?, ?, ?, ?)', 
                 (title, text, source, datetime.now(timezone.utc).isoformat() + 'Z'))
    conn.commit()
    conn.close()

def find_statutes(keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('SELECT * FROM statutes WHERE title LIKE ? OR text LIKE ?', (f'%{keyword}%', f'%{keyword}%'))
    results = cursor.fetchall()
    conn.close()
    return results

def query_with_llm(question):
    statutes = find_statutes(question)
    context = "\n".join([f"{s[1]} ({s[3]}): {s[2]}" for s in statutes]) if statutes else "Статьи не найдены."
    prompt = f"Контекст: {context}\n\nВопрос: {question}\n\nАнализ (Jus Cogens / Erga Omnes):"
    
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return response.text
    except ClientError as e:
        if e.code == 429:
            return "Ошибка квоты (429): Лимит запросов исчерпан. Пожалуйста, подождите 1-2 минуты."
        return f"Ошибка API: {str(e)}"
    except Exception as e:
        return f"Системная ошибка: {str(e)}"

if __name__ == '__main__':
    print("Legal Agent ready.")
