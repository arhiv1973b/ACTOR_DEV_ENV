import os
from pathlib import Path

home = Path.home()
found = []
for p in home.iterdir():
    found.append(str(p))

docs_path = Path("H:/ACTOR_DEV_ENV/docs_found.txt")
docs_path.write_text("\n".join(found), encoding="utf-8")
