import json
import subprocess

log_file = 'audit_log.json'
actor_key = '# [⚖ A©tor Declaration]'

# Чтение лога с принудительной кодировкой UTF-8
with open(log_file, 'r', encoding='utf-8') as f:
    logs = json.load(f)

# Инъекция правового токена в каждую запись
for entry in logs:
    entry['A©TOR_KEY'] = actor_key

# Запись обновленного графа
with open(log_file, 'w', encoding='utf-8') as f:
    json.dump(logs, f, indent=2, ensure_ascii=False)

print("[⚖ A©t0r] Токен A©TOR_KEY успешно внедрен. Регенерация отчета...")

# Автоматический запуск репортера
subprocess.run(['python', 'audit_reporter.py'])
