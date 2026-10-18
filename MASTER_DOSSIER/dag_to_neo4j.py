import json
import os
import sys

# === КОНФИГУРАЦИЯ ===
INPUT_JSON = "VECTOR_ENTITY_EXTRACTION_REPORT.json"
OUTPUT_CYPHER = "neo4j_import_queries.cypher"

def generate_cypher_queries():
    print(f"[*] Инициализация моста-конвертера. Чтение: {INPUT_JSON}...")
    
    if not os.path.exists(INPUT_JSON):
        print(f"[!] ОШИБКА: Файл {INPUT_JSON} не найден.")
        sys.exit(1)

    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("[!] ОШИБКА: Некорректный формат JSON.")
            sys.exit(1)

    queries = []
    
    # 1. Генерация узлов (Nodes: Person, Document, Asset, Institution)
    nodes = data.get("nodes", [])
    print(f"[*] Обнаружено узлов для импорта: {len(nodes)}")
    
    for node in nodes:
        node_id = node.get("id")
        label = node.get("label", "Entity") # Ожидается: Person, Document, Institution и т.д.
        
        # Формирование свойств узла
        properties = node.get("properties", {})
        if "name" in node:
            properties["name"] = node["name"]
            
        props_str_list = []
        for k, v in properties.items():
            # Экранирование строк
            if isinstance(v, str):
                safe_val = v.replace("'", "\\'")
                props_str_list.append(f"{k}: '{safe_val}'")
            else:
                props_str_list.append(f"{k}: {v}")
                
        props_cypher = ", ".join(props_str_list)
        
        query = f"MERGE (n:{label} {{id: '{node_id}'}}) SET n += {{{props_cypher}}};"
        queries.append(query)

    # 2. Генерация связей (Relationships: IDENTIFIES, HOLDS, VERIFIES, BLOCKS)
    edges = data.get("relationships", [])
    print(f"[*] Обнаружено связей для импорта: {len(edges)}")
    
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        rel_type = edge.get("type", "RELATED_TO") # Ожидается: IDENTIFIES, HOLDS...
        
        query = f"""MATCH (source {{id: '{source}'}})
MATCH (target {{id: '{target}'}})
MERGE (source)-[r:{rel_type}]->(target);"""
        queries.append(query)

    # 3. Запись в файл
    with open(OUTPUT_CYPHER, 'w', encoding='utf-8') as out_f:
        out_f.write("\n".join(queries))
        
    print(f"[+] Успех! Cypher-запросы сгенерированы и сохранены в {OUTPUT_CYPHER}")
    print("[*] Вы можете скопировать содержимое этого файла в Neo4j Browser или Bloom.")

if __name__ == "__main__":
    generate_cypher_queries()

