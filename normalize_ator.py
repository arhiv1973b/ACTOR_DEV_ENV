#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
normalize_ator.py
Scans repository files and replaces non-canonical variants of A©tor with the canonical string "A©tor".
"""

import os
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


def normalize_file(filepath):
    try:
        with open(filepath, "rb") as f:
            raw = f.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="replace")

        normalized_text = VARIANT_RE.sub(CANONICAL, text)
        normalized_text = unicodedata.normalize("NFC", normalized_text)

        if normalized_text != text:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(normalized_text)
            print(f"Normalized: {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")


def main():
    for root, dirs, files in os.walk("."):
        if (
            ".git" in root
            or ".venv" in root
            or "node_modules" in root
            or "evidence_vault" in root
        ):
            continue
        for f in files:
            if f.endswith((".md", ".json", ".py", ".html", ".txt", ".yaml", ".yml")):
                if f == "normalize_ator.py":
                    continue
                path = os.path.join(root, f)
                normalize_file(path)
    print("Normalization complete.")


if __name__ == "__main__":
    main()
