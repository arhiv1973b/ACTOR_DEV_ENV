import re
import json

with open("icloud_page.html", "r", encoding="utf-8") as f:
    text = f.read()

# Search for image URLs or JSON data in script tags
print("Searching for photo metadata or URLs...")
urls = re.findall(
    r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|heic|mp4)', text, re.IGNORECASE
)
print(f"Found {len(urls)} direct media URLs:")
for u in set(urls):
    print(" -", u)

# Search for json blobs in script tags
scripts = re.findall(r"<script[^>]*>(.*?)</script>", text, re.DOTALL)
print(f"Total script tags: {len(scripts)}")
for i, s in enumerate(scripts):
    if "photo" in s.lower() or "url" in s.lower() or "icloud" in s.lower():
        print(f"Script {i} length: {len(s)}")
        # Try to find json-like structures
        matches = re.findall(r"(\{.*?\})", s, re.DOTALL)
        if matches:
            print(f"  Found {len(matches)} JSON candidates in script {i}")
