#!/usr/bin/env python3
import os
import shutil
import hashlib
import json
import datetime

doc_path = r"H:\Загрузки\Документ (3) (8).pdf"
vault_dir = r"H:\ACTOR_DEV_ENV\evidence_vault"
dag_manifest_path = r"H:\ACTOR_DEV_ENV\dag_manifest.json"


def ingest():
    if not os.path.exists(doc_path):
        print(f"[-] Source document not found: {doc_path}")
        return

    os.makedirs(vault_dir, exist_ok=True)
    filename = os.path.basename(doc_path)
    dest_path = os.path.join(vault_dir, filename)

    shutil.copy2(doc_path, dest_path)
    print(f"[+] Copied {filename} to vault: {dest_path}")

    # Compute SHA-256
    sha256_hash = hashlib.sha256()
    with open(dest_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()
    print(f"[+] SHA-256: {file_hash}")

    # Update dag_manifest.json
    if os.path.exists(dag_manifest_path):
        with open(dag_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = []

    new_node = {
        "node_id": file_hash[:16],
        "filename": filename,
        "vault_path": dest_path,
        "sha256": file_hash,
        "ingested_at": datetime.datetime.utcnow().isoformat() + "Z",
        "bindings": [
            {
                "framework": "UDHR",
                "article": "17.2",
                "anchor": "90655f14",
                "amount": "25210256.15 MDL",
                "violation_status": "ACTIVE",
            }
        ],
    }

    if isinstance(manifest, list):
        manifest.append(new_node)
    elif isinstance(manifest, dict):
        if "entries" in manifest:
            manifest["entries"].append(new_node)
        elif "nodes" in manifest:
            if isinstance(manifest["nodes"], list):
                manifest["nodes"].append(new_node)
            else:
                manifest["nodes"][new_node["node_id"]] = new_node
        else:
            manifest[new_node["node_id"]] = new_node

    with open(dag_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=4)
    print(f"[+] Added node {new_node['node_id']} to {dag_manifest_path}")


if __name__ == "__main__":
    ingest()
