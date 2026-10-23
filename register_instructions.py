import os

CYPHER_PATH = r"H:\ACTOR_DEV_ENV\register_instructions_graph.cypher"


def main():
    print("Preparing Neo4j Cypher script for Legal Instructions registration...")
    if os.path.exists(CYPHER_PATH):
        with open(CYPHER_PATH, "r", encoding="utf-8") as f:
            query = f.read()
        print("Cypher script loaded successfully.")
        print(query[:300] + "...")
    else:
        print(f"Cypher script not found at {CYPHER_PATH}")


if __name__ == "__main__":
    main()
