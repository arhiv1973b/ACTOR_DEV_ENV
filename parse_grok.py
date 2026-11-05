import json
from pathlib import Path

path = Path("grok_output/network/00247.txt")
text = path.read_text(encoding="utf-8")
parts = text.split("\n\n", 1)
if len(parts) > 1:
    data = json.loads(parts[1])
    print(json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("No JSON part found")
