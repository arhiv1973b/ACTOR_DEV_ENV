import os
import hashlib
import json
import requests
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def download_and_hash(entry, target_dir):
    url = entry["url"]
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            content = response.content
            sha256 = hashlib.sha256(content).hexdigest()
            filename = f"{sha256}.pdf"
            filepath = os.path.join(target_dir, filename)

            with open(filepath, "wb") as f:
                f.write(content)

            entry["sha256"] = sha256
            entry["local_file"] = filename
            entry["status"] = "downloaded"
            return entry
    except Exception as e:
        LOGGER.error(f"Failed to download {url}: {e}")
    entry["status"] = "failed"
    return entry


def run_downloader(registry_json_path, output_dir):
    with open(registry_json_path, "r") as f:
        registry = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(
            executor.map(lambda e: download_and_hash(e, output_dir), registry)
        )

    with open(registry_json_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    run_downloader("exports/registry.json", "exports/downloads")
