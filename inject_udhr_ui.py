#!/usr/bin/env python3
import os
import re

html_block = """
<!-- UDHR ART 17 VIOLATION BLOCK -->
<div style="text-align: center; margin: 40px auto; padding: 20px; max-width: 900px; background-color: #121212; border: 2px solid #ff4444; border-radius: 8px;">
    <h2 style="color: #ff4444; font-family: Consolas, monospace; margin-bottom: 20px;">ANCHOR 90655f14: DIRECT VIOLATION OF UDHR ART. 17.2</h2>
    <img src="dag_udhr17.png" alt="UDHR Article 17 Violation Graph" style="max-width: 100%; height: auto; border: 1px solid #444;">
    <p style="color: #aaaaaa; font-family: Consolas, monospace; font-size: 1.1em; margin-top: 15px;">
        EXPROPRIATED ASSETS: <strong style="color: #ffffff;">25,210,256.15 MDL</strong><br>
        STATUS: ACTIVE / UNRESOLVED
    </p>
</div>
"""

files_to_inject = [
    r"H:\ACTOR_DEV_ENV\apostille-mirror\index.html",
    r"H:\ACTOR_DEV_ENV\apostille-mirror\MASTER_TIMELINE_INDEX.html",
    r"H:\ACTOR_DEV_ENV\timeline.html",
]

for filepath in files_to_inject:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if already injected
        if "UDHR ART 17 VIOLATION BLOCK" not in content:
            new_content = re.sub(r"(?i)</body>", html_block + "\n</body>", content)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[+] Injected violation block into {filepath}")
        else:
            print(f"[*] Already injected in {filepath}")
    else:
        print(f"[-] File not found: {filepath}")
