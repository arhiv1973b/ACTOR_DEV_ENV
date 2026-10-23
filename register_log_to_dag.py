import json
import hashlib
import datetime
import os
import argparse
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

DAG_FILE = "dag_manifest.json"
KEY_DIR = "crypto_keys"
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "artifact_key")
PUBLIC_KEY_PATH = os.path.join(KEY_DIR, "artifact_key.pub")


def calculate_sha256(data_dict):
    """Вычисляет SHA-256 для сериализованного JSON-объекта."""
    json_string = json.dumps(data_dict, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(json_string.encode("utf-8")).hexdigest()


def ensure_ed25519_keys():
    """Создает ключи Ed25519, если они отсутствуют."""
    os.makedirs(KEY_DIR, exist_ok=True)
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        private_key = ed25519.Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_bytes)
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_bytes)


def load_private_key():
    ensure_ed25519_keys()
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def sign_data(private_key, data_bytes):
    signature = private_key.sign(data_bytes)
    return signature.hex()


def load_dag():
    """Загружает существующий DAG или создает генезис-структуру."""
    if os.path.exists(DAG_FILE):
        with open(DAG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "entries" in data:
                return data
            elif isinstance(data, list):
                return {
                    "updated_at": datetime.datetime.now(
                        datetime.timezone.utc
                    ).isoformat(),
                    "total_entries": len(data),
                    "entries": data,
                }
    return {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_entries": 0,
        "entries": [],
    }


def save_dag(dag_container):
    """Сохраняет обновленный DAG контейнер."""
    dag_container["updated_at"] = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()
    dag_container["total_entries"] = len(dag_container["entries"])
    with open(DAG_FILE, "w", encoding="utf-8") as f:
        json.dump(dag_container, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Register log to DAG")
    parser.add_argument(
        "--input", default="evidence_c99741.json", help="Input JSON manifest"
    )
    parser.add_argument("--case", default="MACHERET-1997-2026", help="Case ID")
    args = parser.parse_args()

    dag_container = load_dag()
    entries = dag_container["entries"]

    prev_hash = "GENESIS_NODE"
    if len(entries) > 0:
        prev_hash = entries[-1].get("node_hash", "UNKNOWN")

    input_data = {}
    if os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            input_data = json.load(f)

    payload = {
        "case_id": args.case,
        "manifest_file": args.input,
        "registration_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "protocol": "A©tor Key / TI-ULA / Evidence Anchor [AIPS-2025]",
        "summary": f"DAG registration for Wallet transaction log, Case {args.case}",
        "manifest_data": input_data,
    }

    new_node = {"previous_hash": prev_hash, "payload": payload}

    node_hash = calculate_sha256(new_node)
    new_node["node_hash"] = node_hash

    # Ed25519 cryptographic signature of node_hash
    private_key = load_private_key()
    signature = sign_data(private_key, node_hash.encode("utf-8"))
    new_node["signature_ed25519"] = signature

    entries.append(new_node)
    save_dag(dag_container)
    print(f"Узел успешно зарегистрирован. Хеш: {node_hash}")
    print(f"Ed25519 Подпись: {signature}")

    if "GITHUB_ENV" in os.environ:
        with open(os.environ["GITHUB_ENV"], "a") as env_file:
            env_file.write(f"NEW_NODE_HASH={node_hash}\n")


if __name__ == "__main__":
    main()
