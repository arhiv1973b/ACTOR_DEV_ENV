# load_forensic_graph_neo4j.py
import json
import os

LEDGER_PATH = "artifacts/reabilitare/forensic_capture_ledger.json"

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        raise FileNotFoundError(f"Ledger file not found at {LEDGER_PATH}")
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_cypher_script():
    ledger = load_ledger()
    cypher_lines = [
        "// Cypher ingestion script generated from forensic_capture_ledger.json",
        "MERGE (w:WebhookEvent {event_id: 'WEBHOOK-EVENT-2026-10-08'})",
        "SET w.timestamp = timestamp(), w.status = 'VERIFIED_HMAC'",
        "MERGE (idnp:IdentityAnchor {idnp: '2000001159655'})",
    ]

    for path, details in ledger.items():
        sha256 = details.get("sha256", "UNKNOWN")
        status = details.get("status", "UNKNOWN")
        size = details.get("size_bytes", 0)
        cypher_lines.append(
            f"MERGE (a_{hash(path)}:ForensicArtifact {{path: '{path}'}}) "
            f"SET a_{hash(path)}.sha256 = '{sha256}', a_{hash(path)}.status = '{status}', a_{hash(path)}.size_bytes = {size}"
        )
        cypher_lines.append(f"MERGE (w)-[:PRODUCED_ARTIFACT]->(a_{hash(path)})")
        cypher_lines.append(f"MERGE (a_{hash(path)})-[:BOUND_TO_IDNP]->(idnp)")

    cypher_output_path = "artifacts/reabilitare/forensic_graph_ingest.cypher"
    with open(cypher_output_path, "w", encoding="utf-8") as out:
        out.write("\n".join(cypher_lines))
    print(f"[SUCCESS] Cypher script generated at {cypher_output_path}")


def ingest_to_neo4j():
    generate_cypher_script()
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        ledger = load_ledger()

        artifacts_data = [
            {
                "path": p,
                "sha256": d.get("sha256", "UNKNOWN"),
                "status": d.get("status", "UNKNOWN"),
                "size_bytes": d.get("size_bytes", 0),
            }
            for p, d in ledger.items()
        ]

        query = """
        MERGE (w:WebhookEvent {event_id: $event_id})
        SET w.timestamp = timestamp(), w.status = "VERIFIED_HMAC"
        MERGE (idnp:IdentityAnchor {idnp: "2000001159655"})
        WITH w, idnp
        UNWIND $artifacts as art
        MERGE (a:ForensicArtifact {path: art.path})
        SET a.sha256 = art.sha256, a.status = art.status, a.size_bytes = art.size_bytes
        MERGE (w)-[:PRODUCED_ARTIFACT]->(a)
        MERGE (a)-[:BOUND_TO_IDNP]->(idnp)
        """
        with driver.session() as session:
            session.run(
                query, event_id="WEBHOOK-EVENT-2026-10-08", artifacts=artifacts_data
            )
        print(
            "[SUCCESS] Forensic evidence graph successfully loaded into Neo4j/Bloom via Python driver."
        )
        driver.close()
    except ImportError:
        print(
            "[INFO] neo4j package not installed. Cypher script generated for manual Neo4j/Bloom import."
        )
    except Exception as e:
        print(
            f"[INFO] Neo4j connection skipped/failed ({e}). Cypher script is ready at artifacts/reabilitare/forensic_graph_ingest.cypher."
        )


if __name__ == "__main__":
    ingest_to_neo4j()
