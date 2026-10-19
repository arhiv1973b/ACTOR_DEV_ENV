import os
import json
import urllib.request

MANIFEST_FILE = "apostilles_manifest.json"


def audit_manifest():
    if not os.path.exists(MANIFEST_FILE):
        print("Manifest not found.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        code = item["apostille_code"]
        sec = item.get("security_code", "")
        filename = f"apostille_{code}_{sec}.pdf" if sec else f"apostille_{code}.pdf"

        status = "valid"
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size < 1024:
                status = "tampered_empty"
        else:
            try:
                req = urllib.request.urlopen(item["download_url"], timeout=5)
                if int(req.headers.get("Content-Length", 0)) < 1024:
                    status = "tampered_empty"
            except Exception:
                status = "unreachable"

        item["audit_status"] = status
        print(f"[{status.upper()}] {code} -> {filename}")

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    audit_manifest()
