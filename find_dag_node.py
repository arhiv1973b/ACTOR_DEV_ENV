import json
import os

TARGET_HASH = "b5b9f5cc13267dfa7aa7de63a66abd576d60ba42060dc813b80817853a01b983"
MANIFEST_FILE = "dag_manifest.json"
OUTPUT_FILE = "node_details.json"


def search_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print(f"[-] Файл {MANIFEST_FILE} не найден в текущей директории.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    matches = []

    def recursive_search(obj, parent_key=""):
        if isinstance(obj, dict):
            # Проверяем, является ли текущий словарь узлом
            is_node = any(
                k in obj
                for k in (
                    "hash",
                    "id",
                    "filename",
                    "file_path",
                    "parents",
                    "previous_hashes",
                    "node_hash",
                    "previous_hash",
                )
            )
            if is_node:
                obj_str = json.dumps(obj, ensure_ascii=False)
                if TARGET_HASH in obj_str or TARGET_HASH == parent_key:
                    matches.append((parent_key, obj))

            for k, v in obj.items():
                if k == TARGET_HASH:
                    matches.append((k, obj))
                recursive_search(v, str(k))
        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item, parent_key)

    recursive_search(data)

    # Убираем дубликаты по идентификатору узла
    unique_matches = {}
    for k, v in matches:
        node_id = v.get("hash") or v.get("id") or k
        unique_matches[node_id] = v

    if unique_matches:
        print(f"[+] Найдено узлов/совпадений: {len(unique_matches)}\n")

        # Автоматическое сохранение в node_details.json
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
            json.dump(unique_matches, out_f, ensure_ascii=False, indent=4)
        print(f"[+] Детали успешно сохранены в файл: {OUTPUT_FILE}\n")

        # Вывод в консоль для наглядности
        for node_id, node_data in unique_matches.items():
            print(f"=== Узел (ID/Hash: {node_id}) ===")
            print(json.dumps(node_data, ensure_ascii=False, indent=4))
            print("=" * 60)
    else:
        print(f"[-] Хэш {TARGET_HASH} не найден в файле {MANIFEST_FILE}.")


if __name__ == "__main__":
    search_manifest()
