#!/usr/bin/env python3
"""
UDHR 1948 & Swarm Bridge (udhr_swarm_bridge.py)
Интеграция Всеобщей декларации прав человека 1948 года в онтологический контур Роя и Jus Cogens.
"""

import json
import os
import argparse
from typing import Dict, Any


class UDHRSwarmBridge:
    def __init__(self, json_path: str):
        self.json_path = json_path

    def process(self) -> Dict[str, Any]:
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            doc = data[0] if isinstance(data, list) and len(data) > 0 else data
            articles = doc.get("articles", [])
            total_articles = len(articles)
            title = doc.get("title", "Всеобщая декларация прав человека 1948 г.")
        else:
            total_articles = 30
            title = "Всеобщая декларация прав человека 1948 г."

        return {
            "document": title,
            "total_articles": total_articles,
            "legal_apex": "Неотчуждаемые права человека как императивный базис Jus Cogens и Erga Omnes",
            "ontological_parallel": "Защита человеческого достоинства и свободы от произвола и пыток составляет абсолютный предел государственной власти.",
            "status": "integrated_into_swarm",
        }

    def link_anchor(
        self,
        node_id: str,
        target: str,
        amount: str,
        dag_manifest_path: str = r"H:\ACTOR_DEV_ENV\dag_manifest.json",
    ):
        manifest = []
        if os.path.exists(dag_manifest_path):
            with open(dag_manifest_path, "r", encoding="utf-8") as f:
                try:
                    manifest = json.load(f)
                except Exception:
                    manifest = []

        anchor_node = {
            "node_id": node_id,
            "type": "STOLEN_ASSETS_ANCHOR",
            "attributes": {
                "amount": amount,
                "currency": "MDL",
                "status": "EXPROPRIATED",
            },
            "bindings": [
                {
                    "framework": "UDHR",
                    "article": "17.2",
                    "text": "Никто не должен быть произвольно лишен своего имущества.",
                    "violation_status": "ACTIVE",
                }
            ],
            "edges": [{"target": target, "relation": "DIRECT_VIOLATION"}],
        }

        # Check if already exists, update or append
        found = False
        if isinstance(manifest, list):
            for i, item in enumerate(manifest):
                if isinstance(item, dict) and item.get("node_id") == node_id:
                    manifest[i] = anchor_node
                    found = True
                    break
            if not found:
                manifest.append(anchor_node)
        elif isinstance(manifest, dict):
            if "nodes" in manifest and isinstance(manifest["nodes"], list):
                for i, item in enumerate(manifest["nodes"]):
                    if isinstance(item, dict) and item.get("node_id") == node_id:
                        manifest["nodes"][i] = anchor_node
                        found = True
                        break
                if not found:
                    manifest["nodes"].append(anchor_node)
            else:
                manifest[node_id] = anchor_node

        with open(dag_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=4)
        print(
            f"[+] Anchor {node_id} successfully linked to {target} with amount {amount} MDL in {dag_manifest_path}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDHR Swarm Bridge & Anchor Linker")
    parser.add_argument("--link-anchor", help="Node ID to link")
    parser.add_argument("--target", help="Target node/framework (e.g. UDHR_17.2)")
    parser.add_argument("--amount", help="Amount value")
    args = parser.parse_args()

    bridge = UDHRSwarmBridge(
        r"H:\ACTOR_DEV_ENV\inbox\Всеобщая_декларация_прав_Человека_1948.json"
    )

    if args.link_anchor:
        bridge.link_anchor(
            args.link_anchor, args.target or "UDHR_17.2", args.amount or "25210256.15"
        )
    else:
        result = bridge.process()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(
            "\n🕊️ Всеобщая декларация прав человека (1948) успешно интегрирована в контур Роя."
        )
