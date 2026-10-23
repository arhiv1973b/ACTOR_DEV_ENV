import hashlib
import os

files = [
    ("backup_215110", r"H:\ACTOR_DEV_ENV\dag_manifest_backup_20261001_215110.json"),
    ("backup_220254", r"H:\ACTOR_DEV_ENV\dag_manifest_backup_20261001_220254.json"),
    ("dag_manifest", r"H:\ACTOR_DEV_ENV\dag_manifest.json"),
    ("udhr_claim_manifest", r"H:\ACTOR_DEV_ENV\udhr_claim_manifest.json"),
    ("dag_udhr17_png", r"H:\ACTOR_DEV_ENV\dag_udhr17.png"),
]

for name, path in files:
    if os.path.exists(path):
        with open(path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        print(f"{name}: {h}", flush=True)
    else:
        print(f"{name}: MISSING", flush=True)
