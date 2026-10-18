import urllib.request
import re
import json
import yaml
from urllib.parse import urljoin

url = "https://arhiv1973b.github.io/apostille-archive-english/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode("utf-8")
except Exception as e:
    print(f"Error fetching {url}: {e}")
    exit(1)

hrefs = re.findall(r'href="([^"]+\.pdf)"', html)
apostilles = []

for h in hrefs:
    # filename pattern: apostille_<code>_<security>.pdf
    match = re.search(r'apostille_([A-Z0-9]+)_([0-9]+)\.pdf', h)
    if match:
        code = match.group(1)
        sec_code = match.group(2)
        download_url = urljoin(url, h)
        apostilles.append({
            "apostille_code": code,
            "security_code": sec_code,
            "download_url": download_url
        })

data = {
    "apostilles": apostilles,
    "total_expected": 97,
    "total_real_downloadable": len(apostilles),
    "defect_reason": "7 records missing or filtered on GitHub, but preserved in master PDF archive"
}

with open("apostilles_registry_90.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open("apostilles_registry_90.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print(f"Successfully generated manifests with {len(apostilles)} records.")
