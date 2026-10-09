import os
import hashlib
import json

path = r"H:\Загрузки\Aviza..pdf"
if os.path.exists(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    sha = h.hexdigest()
    size = os.path.getsize(path)
    print(f"File: {path}")
    print(f"SHA-256: {sha}")
    print(f"Size: {size}")

    # Update manifest
    manifest_path = r"H:\ACTOR_DEV_ENV\downloads_evidence_manifest_07102026.json"
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"evidence_items": []}

    # Check if already present
    exists = False
    for item in data.get("evidence_items", []):
        if item.get("path") == path:
            item["sha256"] = sha
            item["size_bytes"] = size
            item["status"] = "verified_exists"
            exists = True
            break
    if not exists:
        data.setdefault("evidence_items", []).append(
            {
                "path": path,
                "filename": os.path.basename(path),
                "sha256": sha,
                "size_bytes": size,
                "status": "verified_exists",
            }
        )

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Manifest updated successfully.")
else:
    print(f"File not found: {path}")
