import json, urllib.request, ssl
from pathlib import Path

MANIFEST = Path("manifest.json")
BASE_URL = "https://arhiv1973b.github.io/apostille-archive-english/"
THRESHOLD = 1024 

def check_link(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=5) as r:
            return int(r.headers.get("Content-Length", 0)) > THRESHOLD
    except: return False

def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"{'CODE':<15} | {'STATUS':<20} | {'REMOTE'}")
    print("-" * 50)
    for rec in data["records"]:
        url = BASE_URL + rec["filename"]
        is_valid = check_link(url)
        print(f"{rec['code']:<15} | {rec['status']:<20} | {'OK' if is_valid else '!!! 40 BYTES/ERR'}")

if __name__ == "__main__":
    main()
