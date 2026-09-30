import os
import time
import subprocess
from datetime import datetime

def run_pipeline():
    print(f"[{datetime.now()}] [WATCHER] Обнаружено изменение. Запуск форензик-пайплайна...")
    try:
        # 1. Запуск генерации экспертного отчета
        subprocess.run(["python", "export_expert_report.py"], check=True)
        print(f"[{datetime.now()}] [WATCHER] Экспертный отчет успешно пересоздан.")
    except Exception as e:
        print(f"[{datetime.now()}] [WATCHER] Ошибка выполнения пайплайна: {e}")

def watch_directory():
    path = r"H:\ACTOR_DEV_ENV"
    print(f"--- [TI-ULA WATCHER ЗАПУЩЕН] Мониторинг директории: {path} ---")
    
    # Отслеживаем время изменения ключевых файлов
        
    watched_files = ["dag_manifest.json", "EVIDENCE_REGISTRY_INDEX.json"]
    last_mtimes = {}
    
    for wf in watched_files:
        full_p = os.path.join(path, wf)
        if os.path.exists(full_p):
            last_mtimes[wf] = os.path.getmtime(full_p)

    while True:
        time.sleep(5)
        for wf in watched_files:
            full_p = os.path.join(path, wf)
            if os.path.exists(full_p):
                current_mtime = os.path.getmtime(full_p)
                if wf not in last_mtimes or current_mtime != last_mtimes[wf]:
                    print(f"[{datetime.now()}] Изменен файл: {wf}")
                    last_mtimes[wf] = current_mtime
                    run_pipeline()

if __name__ == "__main__":
    watch_directory()
