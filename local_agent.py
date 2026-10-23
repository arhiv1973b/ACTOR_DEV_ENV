import os
import subprocess

def run_local_audit():
    print("🚀 [LOCAL MODE] Запуск аудита без внешних API...")
    cmd = ["python3", "conflict_risk_analyzer.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stderr:
        print(f"⚠️ Системный лог ошибок: {result.stderr}")
        
    return result.stdout

if __name__ == "__main__":
    report = run_local_audit()
    
    # Именно эта строка заставит скрипт вывести результат в консоль
    print(report) 
    
    with open("conflict_risk_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Аудит завершен локально. Отчет: conflict_risk_report.md")
