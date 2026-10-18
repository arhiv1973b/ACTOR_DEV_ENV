import re
import json

with open("icloud_page.html", "r", encoding="utf-8") as f:
    text = f.read()

# Look for shared stream data or webservices URLs
matches = re.findall(r'https?://[^\s<>"]+', text)
print(f"Total URLs found in page: {len(matches)}")
for m in matches:
    if "p" in m or "icloud" in m or "apple" in m or "stream" in m:
        if len(m) < 150:
            print("  URL:", m)
