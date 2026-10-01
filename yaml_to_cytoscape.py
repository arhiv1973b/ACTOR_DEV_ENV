import os
import json
import yaml
import hashlib
import subprocess

INPUT_YAML = r"H:\ACTOR_DEV_ENV\data\whitehouse_fincombank_audit.yaml"
OUTPUT_JSON = r"H:\ACTOR_DEV_ENV\whitehouse_fincombank_cytoscape.json"

def main():
    if not os.path.exists(INPUT_YAML):
        print(f"Error: {INPUT_YAML} not found.")
        return

    with open(INPUT_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Convert nodes and edges into Cytoscape elements structure
    elements = []
    for node in data.get("nodes", []):
        elements.append({
            "data": {
                "id": node.get("id"),
                "name": node.get("name"),
                "role": node.get("role"),
                "type": node.get("type", "default")
            }
        })

    for edge in data.get("edges", []):
        edge_data = {
            "source": edge.get("source"),
            "target": edge.get("target"),
            "label": edge.get("label")
        }
        classes = edge.get("classes")
        element_dict = {"data": edge_data}
        if classes:
            element_dict["classes"] = classes
        elements.append(element_dict)

    cytoscape_container = {
        "metadata": data.get("node", {}),
        "elements": elements
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(cytoscape_container, f, ensure_ascii=False, indent=2)

    print(f"[✓] Generated Cytoscape JSON at: {OUTPUT_JSON}")

    # Compute SHA-256 hash of generated JSON
    with open(OUTPUT_JSON, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"[✓] SHA-256 Hash of Cytoscape JSON: {file_hash}")

    # Automatically register to DAG via register_log_to_dag.py
    dag_script = r"H:\ACTOR_DEV_ENV\register_log_to_dag.py"
    if os.path.exists(dag_script):
        print("[*] Registering node to DAG via register_log_to_dag.py...")
        subprocess.run(["python", dag_script, "--input", OUTPUT_JSON, "--case", "CASE-MACHERET-1997-2026"], check=True)
    else:
        print("[!] register_log_to_dag.py not found for automatic DAG registration.")

if __name__ == "__main__":
    main()
