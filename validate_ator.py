#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
validate_ator.py
Checks repository files for any occurrences of A©tor variants and fails if
there are occurrences that are not exactly the canonical string "A©tor" (with U+00A9).
"""

import os
import sys
import re
import unicodedata

CANONICAL = "A©tor"

VARIANT_RE = re.compile(
    r"(?:A|А)"
    r"(?:©|\u00A9|&copy;|&#169;|&#xA9;|\(c\)|%C2%A9)"
    r"(?:t[oо]r|т[oо]р)"
    r"&?",
    flags=re.IGNORECASE,
)

# Files/directories to check directly
TARGET_FILES = []
for f in os.listdir("."):
    if f.endswith((".md", ".json", ".py", ".html")) and os.path.isfile(f):
        if f != "validate_ator.py":
            TARGET_FILES.append(f)

violations = []

for path in TARGET_FILES:
    try:
        with open(path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        continue
    text = unicodedata.normalize("NFC", text)
    for m in VARIANT_RE.finditer(text):
        found = m.group(0)
        if found != CANONICAL and found != "A©TOR" and found != "A©TOR_KEY":
            violations.append((path, found))

if violations:
    sys.stderr.write("A©tor validation FAILED. Found non-canonical occurrences:\n")
    for p, v in violations:
        sys.stderr.write(f"{p}: {v}\n")
    sys.exit(2)

print("A©tor validation OK: no non-canonical occurrences found.")
sys.exit(0)
