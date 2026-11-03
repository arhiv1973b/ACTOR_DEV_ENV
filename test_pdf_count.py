#!/usr/bin/env python3
from pathlib import Path

root = Path(r"H:\ACTOR_DEV_ENV")
pdfs = list(root.glob("**/*.pdf"))
print(f"Total PDFs found: {len(pdfs)}")
for p in pdfs[:20]:
    print(p, p.stat().st_size)
print("...")
for p in pdfs[20:]:
    if p.stat().st_size > 50 * 1024 * 1024:  # > 50MB
        print("Large PDF:", p, p.stat().st_size / (1024 * 1024), "MB")
print("Done listing.")
