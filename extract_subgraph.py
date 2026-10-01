import json
import os

TARGET_HASH = "b5b9f5cc13267dfa7aa7de63a66abd576d60ba42060dc813b80817853a01b983"
MANIFEST_FILE = "dag_manifest.json"
OUTPUT_SUB_MANIFEST = "sub_manifest.json"

def extract_subgraph():
    if not os.path.exists(MANIFEST_FILE):
        print(f"[-] Файл {MANIFEST_FILE} не найден в текущей директории.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Индексация всех узлов графа
    node_map = {}
    
    def index_nodes(obj):
        if isinstance(obj, dict):
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

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                node_map[k] = v

    if TARGET_HASH not in node_map:
        print(f"[-] Целевой узел с хэшем {TARGET_HASH} не найден в манифесте.")
        return

    def get_parents(node):
        p_field = node.get("parents") or node.get("parent_hashes") or node.get("previous_hashes") or []
        if isinstance(p_field, str):
            p_field = [p_field]
        parents_list = list(p_field)
        if node.get("previous_hash"):
            parents_list.append(node.get("previous_hash"))
        return list(set(parents_list))

    # Обход графа вверх по цепочке родителей (BFS)
    subgraph_nodes = {}
    queue = [TARGET_HASH]
    visited = set()

    while queue:
        current_hash = queue.pop(0)
        if current_hash in visited:
            continue
        visited.add(current_hash)

        node = node_map.get(current_hash)
        if node:
            subgraph_nodes[current_hash] = node
            for parent_hash in get_parents(node):
                if parent_hash and parent_hash != "GENESIS_NODE" and parent_hash not in visited:
                    queue.append(parent_hash)

    # Сохранение подмножества в мини-манифест
    with open(OUTPUT_SUB_MANIFEST, "w", encoding="utf-8") as out_f:
        json.dump(subgraph_nodes, out_f, ensure_ascii=False, indent=4)

    print(f"[+] Подмножество графа успешно сформировано!")
    print(f"[+] Узлов в изолированной ветке: {len(subgraph_nodes)}")
    print(f"[+] Мини-манифест сохранен в файл: {OUTPUT_SUB_MANIFEST}")

if __name__ == "__main__":
    extract_subgraph()
