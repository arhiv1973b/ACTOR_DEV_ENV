import json
import os

TARGET_HASH = "b5b9f5cc13267dfa7aa7de63a66abd576d60ba42060dc813b80817853a01b983"
MANIFEST_FILE = "dag_manifest.json"
OUTPUT_REPORT = "lineage_report.json"

def trace_ancestry():
    if not os.path.exists(MANIFEST_FILE):
        print(f"[-] Файл {MANIFEST_FILE} не найден в текущей директории.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Универсальная нормализация структуры манифеста в список узлов или словарь хэш->узел
    node_map = {}
    
    def index_nodes(obj):
        if isinstance(obj, dict):
            # Проверяем, является ли текущий словарь узлом DAG
            if any(k in obj for k in ("hash", "id", "node_hash", "filename", "file_path", "parents", "parent_hashes", "previous_hashes", "previous_hash")):
                h = obj.get("node_hash") or obj.get("hash") or obj.get("id")
                if h:
                    node_map[h] = obj
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    index_nodes(v)
                elif isinstance(v, dict) and k not in node_map:
                    node_map[k] = v
        elif isinstance(obj, list):
            for item in obj:
                index_nodes(item)

    index_nodes(data)

    # Если манифест — корневой словарь, где ключи это хэши
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                node_map[k] = v

    if TARGET_HASH not in node_map:
        print(f"[-] Целевой узел с хэшем {TARGET_HASH} не найден в индексе манифеста.")
        return

    print(f"[+] Найден целевой узел. Запуск трассировки предков вверх по графу...\n")

    def get_parents(node):
        p_field = node.get("parents") or node.get("parent_hashes") or node.get("previous_hashes") or []
        if isinstance(p_field, str):
            p_field = [p_field]
        parents_list = list(p_field)
        if node.get("previous_hash"):
            parents_list.append(node.get("previous_hash"))
        return list(set(parents_list))

    # обход вверх с поиском в ширину/глубину для сбора всей цепочки
    ancestors = []
    queue = [TARGET_HASH]
    visited = set()

    while queue:
        current_hash = queue.pop(0)
        if current_hash in visited:
            continue
        visited.add(current_hash)

        node = node_map.get(current_hash)
        if node:
            doc_ref = node.get("filename") or node.get("file_path") or (node.get("payload") and node.get("payload").get("document_ref")) or "N/A"
            ancestors.append({
                "hash": current_hash,
                "filename": doc_ref,
                "tags": node.get("tags", []),
                "metadata": node.get("metadata", {}),
                "parents": get_parents(node)
            })
            for parent_hash in get_parents(node):
                if parent_hash and parent_hash != "GENESIS_NODE" and parent_hash not in visited:
                    queue.append(parent_hash)

    # Вывод результатов в консоль
    print(f"=== ОТЧЕТ О РОДОСЛОВНОЙ УЗЛА (Всего узлов в цепочке: {len(ancestors)}) ===\n")
    for idx, item in enumerate(ancestors):
        print(f"[{idx}] Hash: {item['hash']}")
        print(f"    Файл: {item['filename']}")
        print(f"    Теги: {item['tags']}")
        if item['parents']:
            print(f"    Родители: {', '.join(item['parents'])}")
        else:
            print(f"    (Корневой исходный документ / Начало ветки)")
        print("-" * 60)

    # Сохранение полного отчета в файл
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as out_f:
        json.dump(ancestors, out_f, ensure_ascii=False, indent=4)
    print(f"\n[+] Полная цепочка предков успешно сохранена в файл: {OUTPUT_REPORT}")

if __name__ == "__main__":
    trace_ancestry()
