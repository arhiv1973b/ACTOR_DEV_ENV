import shutil, os

src_root = r"H:\ACTOR_DEV_ENV"
dst_root = r"H:\ACTOR_DEV_ENV\maceret-case-evidence"

for d in ["docs", "proofs", "scripts", ".github"]:
    s_dir = os.path.join(src_root, d)
    d_dir = os.path.join(dst_root, d)
    try:
        if os.path.exists(d_dir):
            shutil.rmtree(d_dir)
        shutil.copytree(s_dir, d_dir)
        print(f"COPIED: {d}")
    except Exception as e:
        print(f"ERROR: {d} -> {e}")
