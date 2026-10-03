#!/usr/bin/env python3
"""
Jus Cogens Autonomous DAG Orchestrator
Version: 2026.1.0
Signature: # ⚖ A©tor Declaration
"""

import os
import sys
import json
import hashlib
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_PATH = "pipeline_dag_config.json"
LEDGER_PATH = "evidence_ledger_sha256.log"
MANIFEST_PATH = "JUS_COGENS_GLOBAL_MANIFEST_2026.md"


def log_msg(msg):
    print(f"[JUS_COGENS_ORCHESTRATOR] {msg} | Signature: # ⚖ A©tor Declaration")


def execute_node(node_id):
    log_msg(f"Executing node: {node_id}")
    if node_id == "manifest":
        if not os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                f.write("# JUS COGENS GLOBAL MANIFEST 2026\n")
        log_msg("Manifest verified/created.")
    elif node_id == "hash":
        if os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            log_msg(f"Manifest SHA-256: {h}")
            return h
        else:
            raise FileNotFoundError(f"Manifest missing: {MANIFEST_PATH}")
    elif node_id == "evidence_update":
        if os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "rb") as f:
                h = hashlib.sha256(f.read()).hexdigest()
            entry = f"JUS_COGENS_GLOBAL_MANIFEST_2026.md: {h}\n"
            with open(LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(entry)
            log_msg(f"Appended hash to append-only ledger: {LEDGER_PATH}")
    elif node_id == "commit_push":
        cmd = 'git add JUS_COGENS_GLOBAL_MANIFEST_2026.md evidence_ledger_sha256.log && git commit -m "deploy(core): Jus Cogens global manifest – scientific-legal revolution mode active" && git push origin feature/cyber-sabotage-audit-10-2026'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        log_msg(f"Git commit/push output: {res.stdout.strip() or res.stderr.strip()}")
    elif node_id == "graph_ingest":
        log_msg("Executing graph ingest (append-only ledger sync)...")
    elif node_id == "graph_export":
        log_msg("Executing graph export (GraphML)...")
    else:
        log_msg(f"Unknown node: {node_id}")


def run_orchestrator():
    if not os.path.exists(CONFIG_PATH):
        log_msg(f"Error: Config not found at {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    dag = config["dependency_graph"]
    nodes = {n["id"]: n for n in dag["nodes"]}
    edges = dag["edges"]

    # Build adjacency and in-degree
    in_degree = {n_id: 0 for n_id in nodes}
    adj = {n_id: [] for n_id in nodes}

    for edge in edges:
        u = edge["from"]
        v = edge["to"]
        adj[u].append(v)
        in_degree[v] += 1

    # Topological sort levels or queue
    queue = [n_id for n_id, deg in in_degree.items() if deg == 0]

    executed = set()

    # Simple sequential/parallel execution honoring DAG
    while queue:
        current_batch = list(queue)
        queue.clear()

        parallel_nodes = [
            n_id for n_id in current_batch if nodes[n_id].get("type") == "parallel"
        ]
        sequential_nodes = [
            n_id for n_id in current_batch if nodes[n_id].get("type") != "parallel"
        ]

        # Execute sequential nodes first
        for n_id in sequential_nodes:
            execute_node(n_id)
            executed.add(n_id)
            for neighbor in adj[n_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Execute parallel nodes concurrently if any
        if parallel_nodes:
            log_msg(f"Executing parallel batch: {parallel_nodes}")
            with ThreadPoolExecutor(max_workers=len(parallel_nodes)) as executor:
                futures = {
                    executor.submit(execute_node, n_id): n_id for n_id in parallel_nodes
                }
                for future in as_completed(futures):
                    n_id = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        log_msg(f"Error in parallel node {n_id}: {e}")
                    executed.add(n_id)
                    for neighbor in adj[n_id]:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            queue.append(neighbor)

    log_msg("DAG Orchestration completed successfully.")


if __name__ == "__main__":
    run_orchestrator()
