#!/usr/bin/env python3
# A©TOR_KEY="# [⚖ A©tor Declaration]"
import json
import os
import hashlib


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_merkle_root(leaves):
    if not leaves:
        return sha256_hex(b"empty")

    current_level = sorted(list(set(leaves)))

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            combined = (left + right).encode("utf-8")
            next_level.append(sha256_hex(combined))
        current_level = next_level

    return current_level[0]


def main():
    root = "correspondence-archive"
    index_path = os.path.join(root, "index.json")
    integrity_path = os.path.join(root, "INTEGRITY.json")

    leaves = []
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("items", []):
                h = item.get("sha256")
                if h:
                    leaves.append(h)

    ev_manifest = "evidence-vault/apostilles_manifest.json"
    if os.path.exists(ev_manifest):
        with open(ev_manifest, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
            for entry in manifest_data[:10]:
                code = entry.get("apostille_code", "")
                sec = entry.get("security_code", "")
                if code:
                    leaves.append(sha256_hex(f"{code}:{sec}".encode("utf-8")))

    evidence_path = "evidence"
    if os.path.exists(evidence_path):
        for fname in os.listdir(evidence_path):
            if fname.endswith(".md"):
                fpath = os.path.join(evidence_path, fname)
                with open(fpath, "rb") as ef:
                    leaves.append(sha256_hex(ef.read()))

    merkle_root = compute_merkle_root(leaves)
    print(
        f"[*] Re-computed Merkle Root (with evidence leaves): {merkle_root} (from {len(leaves)} leaves)"
    )

    merkle_data = {
        "merkle_version": "1.0.0",
        "actor_key": "# [⚖ A©tor Declaration]",
        "leaf_count": len(leaves),
        "merkle_root": merkle_root,
        "leaves": leaves,
    }

    merkle_json_path = os.path.join(root, "merkle.json")
    with open(merkle_json_path, "w", encoding="utf-8") as f:
        json.dump(merkle_data, f, indent=2)
    print(f"[+] Updated {merkle_json_path}")

    if os.path.exists(integrity_path):
        with open(integrity_path, "r", encoding="utf-8") as f:
            integ = json.load(f)
        integ["merkle_root"] = merkle_root
        with open(integrity_path, "w", encoding="utf-8") as f:
            json.dump(integ, f, indent=2)
        print(f"[+] Updated {integrity_path} with new merkle_root")


if __name__ == "__main__":
    main()
