import os
import sys
import subprocess
import json
from datetime import datetime
from gearbox_rotator import execute_with_gearbox

def run_audit_and_sync():
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = sys.stdin.read().strip()
    
    if not prompt:
        prompt = "Сделай краткий аудит системы и выведи статус"

    print(f"[Audit Sync] Запуск запроса к Gearbox...")
    result = execute_with_gearbox(prompt)
    
    if not result:
        print("[Error] Не удалось получить ответ от моделей.")
        sys.exit(1)
        
    print("\n--- Результат выполнения ---")
    print(result)

    # Создаем директорию для логов аудита
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audit_dir = os.path.join(base_dir, "audit_logs")
    os.makedirs(audit_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"audit_{timestamp}.md"
    report_path = os.path.join(audit_dir, report_filename)
    
    # Записываем отчет
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Audit Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Prompt:** {prompt}\n\n---\n\n{result}\n")
        
    print(f"[Audit Sync] Отчет сохранен: audit_logs/{report_filename}")

    # Git автоматизация
    try:
        print("[Git Sync] Добавление отчета в индекс Git...")
        subprocess.run(["git", "add", report_path], check=True, cwd=base_dir)
        
        commit_msg = f"chore(audit): auto-sync audit report {timestamp}"
        print(f"[Git Sync] Создание коммита: '{commit_msg}'...")
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=base_dir)
        
        print("[Git Sync] Отправка изменений в ветку model-hub-sync...")
        subprocess.run(["git", "push", "origin", "model-hub-sync"], check=True, cwd=base_dir)
        print("[Git Sync] Синхронизация с удаленным репозиторием завершена успешно!")
    except subprocess.CalledProcessError as e:
        print(f"[Git Error] Ошибка при выполнении Git-операций: {e}")

if __name__ == "__main__":
    run_audit_and_sync()
