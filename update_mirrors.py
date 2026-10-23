import os
import shutil

src = r"H:\ACTOR_DEV_ENV\apostille_80UQ636YBZG17_2013073978518.pdf"
dest_dirs = [
    r"H:\ACTOR_DEV_ENV\apostille-mirror\mirrors",
    r"H:\ACTOR_DEV_ENV\apostille-archive-english",
]

variants = [
    "apostille_80UQ636YBZG17_2013073978518.pdf",
    "apostille_8OUQ636YBZGI7_2013073978518.pdf",
    "8OUQ636YBZGI7_EVIDENCE.pdf",
]

for d in dest_dirs:
    os.makedirs(d, exist_ok=True)
    for v in variants:
        dest = os.path.join(d, v)
        if os.path.abspath(src) != os.path.abspath(dest):
            shutil.copy2(src, dest)
            print(f"Copied to {dest}")
print("All mirrors updated successfully.")
