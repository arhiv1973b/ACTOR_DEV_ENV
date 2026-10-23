import json
import os

dataset_path = 'H:\\ACTOR_DEV_ENV\\agent_dataset.jsonl'

# Базовые примеры для обучения агента специфике TI-ULA
training_data = [
    {
        "messages": [
            {"role": "system", "content": "Ты автономный локальный агент. Вызывай функции в формате JSON."},
            {"role": "user", "content": "Проверь целостность файла evidence_manifest.json"},
            {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "get_file_hash", "arguments": {"filepath": "evidence_manifest.json"}}}]}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "Ты автономный локальный агент. Вызывай функции в формате JSON."},
            {"role": "user", "content": "Извлеки метаданные из DICOM-снимка для реестра"},
            {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "audit_dicom_meta", "arguments": {"filepath": "scan.dcm"}}}]}
        ]
    },
    {
        "messages": [
            {"role": "system", "content": "Ты автономный локальный агент. Вызывай функции в формате JSON."},
            {"role": "user", "content": "Сформируй манифест для нового узла"},
            {"role": "assistant", "content": "", "tool_calls": [{"function": {"name": "create_manifest", "arguments": {"node_id": "Aйtor_01", "status": "verified"}}}]}
        ]
    }
]

with open(dataset_path, 'w', encoding='utf-8') as f:
    for item in training_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"\n✅ Тренировочный датасет успешно создан: {dataset_path}")
print(f"Добавлено базовых записей: {len(training_data)}\n")
