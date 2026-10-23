import os
import hashlib
import json

path = r"C:\Users\arhiv\OneDrive\Документы\ViberDownloads\0-02-05-5e95ca6ac4382738878632a6f6e933aae157be5d9253fbc2f3d449ead5bcde53_b668fae3f68e1fab.jpg"
hash_val = "FILE_NOT_FOUND"
size = 0
if os.path.exists(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    hash_val = h.hexdigest()
    size = os.path.getsize(path)

print(f"File: {path}")
print(f"SHA-256: {hash_val}")
print(f"Size: {size}")
