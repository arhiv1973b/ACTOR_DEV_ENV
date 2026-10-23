import json
import re
from datetime import datetime, timezone

log_path = "msmtp_dispatch_log.txt"
timeline_path = "evidence_timeline.json"

# 1. Чтение последних записей из лога отправки
try:
    with open(log_path, "r", encoding="utf-8") as f:
        log_lines = f.readlines()
except FileNotFoundError:
    print(f"❌ Ошибка: Файл {log_path} не найден.")
    exit(1)

# Фильтрация и парсинг строк лога (ожидаемый формат: [YYYY-MM-DDTHH:MM:SSZ] DISPATCH: ...)
new_events = []
iso_pattern = re.compile(
    r"\[(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)\]\s+DISPATCH:\s+(.*)"
)

for line in log_lines:
    match = iso_pattern.search(line)
    if match:
        timestamp_str, description = match.groups()
        new_events.append(
            {
                "timestamp": timestamp_str,
                "event": "Dispatch Legal Submission",
                "actor": "Alexei Macheret",
                "channel": "msmtp / SMTP",
                "details": description.strip(),
                "status": "Verified / Transmitted",
            }
        )

if not new_events:
    print("⚠️ В msmtp_dispatch_log.txt не найдено новых записей для интеграции.")
    exit(0)

# 2. Загрузка существующего графа доказательств / таймлайна
try:
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Если файл отсутствует или пуст, инициализируем базовую структуру
    timeline_data = {"project_id": "CASE-MACHERET-1997-2026", "timeline_events": []}

# Поддержка различных ключей структуры таймлайна (events или timeline_events)
events_key = "timeline_events" if "timeline_events" in timeline_data else "events"
if events_key not in timeline_data:
    timeline_data[events_key] = []

# 3. Интеграция новых событий с защитой от дубликатов
existing_timestamps = {e.get("timestamp") for e in timeline_data[events_key]}
added_count = 0

for event in new_events:
    if event["timestamp"] not in existing_timestamps:
        timeline_data[events_key].append(event)
        existing_timestamps.add(event["timestamp"])
        added_count += 1

# Сортировка событий по хронологии
timeline_data[events_key].sort(key=lambda x: x.get("timestamp", ""))

# 4. Сохранение обновленного evidence_timeline.json
with open(timeline_path, "w", encoding="utf-8") as f:
    json.dump(timeline_data, f, indent=4, ensure_ascii=False)

print(f"✅ Успешно интегрировано новых событий в {timeline_path}: {added_count}")
