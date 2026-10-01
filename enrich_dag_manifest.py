import json
import os
from datetime import datetime

LEGAL_FINDINGS_FILE = "legal_findings_contextual.json"
DAG_MANIFEST_FILE = "dag_manifest.json"

def enrich_dag_manifest():
    if not os.path.exists(LEGAL_FINDINGS_FILE):
        print(f"[-] Файл {LEGAL_FINDINGS_FILE} не найден.")
        return
        
    if not os.path.exists(DAG_MANIFEST_FILE):
        print(f"[-] Файл {DAG_MANIFEST_FILE} не найден.")
        return

    # 1. Загрузка данных
    with open(LEGAL_FINDINGS_FILE, "r", encoding="utf-8") as f:
        findings = json.load(f)
        
    with open(DAG_MANIFEST_FILE, "r", encoding="utf-8") as f:
        dag_manifest = json.load(f)

    # Словарь для быстрого поиска по имени файла
    findings_map = {item["filename"]: item["matches"] for item in findings}
    
    # 2. Создание резервной копии
    backup_file = f"dag_manifest_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(dag_manifest, f, ensure_ascii=False, indent=4)
    print(f"[*] Создана резервная копия: {backup_file}")

    updated_count = 0

    # 3. Обновление манифеста (универсальная обработка структуры)
    nodes_list = []
    if isinstance(dag_manifest, list):
        nodes_list = dag_manifest
    elif isinstance(dag_manifest, dict):
        if "entries" in dag_manifest and isinstance(dag_manifest["entries"], list):
            nodes_list = dag_manifest["entries"]
        elif "nodes" in dag_manifest and isinstance(dag_manifest["nodes"], list):
            nodes_list = dag_manifest["nodes"]
        elif "nodes" in dag_manifest and isinstance(dag_manifest["nodes"], dict):
            nodes_list = list(dag_manifest["nodes"].values())
        else:
            nodes_list = list(dag_manifest.values())

    for node in nodes_list:
        if isinstance(node, dict):
            filename = extract_filename(node)
            if filename in findings_map:
                update_node(node, findings_map[filename])
                updated_count += 1

    # 4. Сохранение результата
    with open(DAG_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(dag_manifest, f, ensure_ascii=False, indent=4)

    print(f"[+] Обновлено узлов: {updated_count}")
    print(f"[+] Изменения сохранены в {DAG_MANIFEST_FILE}")

def extract_filename(node):
    """Извлекает имя файла из узла, независимо от структуры."""
    path = (
        node.get("filename") or 
        node.get("file_path") or 
        node.get("payload", {}).get("document_ref") or 
        node.get("document_ref", "")
    )
    return path.split("/")[-1].split("\\")[-1]

def update_node(node, matches):
    """Внедряет юридические метаданные и проставляет теги."""
    if "metadata" not in node:
        node["metadata"] = {}
        
    if "legal_context" not in node["metadata"]:
        node["metadata"]["legal_context"] = {}

    ctx = node["metadata"]["legal_context"]
    
    ctx["dates"] = list(set(ctx.get("dates", []) + matches.get("contextual_dates", [])))
    ctx["terms"] = list(set(ctx.get("terms", []) + matches.get("legal_terms", [])))
    ctx["names"] = list(set(ctx.get("names", []) + matches.get("names", [])))

    node["tags"] = list(set(node.get("tags", []) + ["legal_evidence", "ocr_processed"]))

if __name__ == "__main__":
    enrich_dag_manifest()
