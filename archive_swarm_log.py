import os
import shutil
import hashlib
from datetime import datetime


def main():
    log_src = os.path.abspath("swarm-deploy.log")
    mirror_dir = os.path.abspath("apostille-mirror/logs")
    if not os.path.exists(mirror_dir):
        os.makedirs(mirror_dir)

    log_dest = os.path.join(mirror_dir, "swarm-deploy.log")
    if os.path.exists(log_src):
        shutil.copy2(log_src, log_dest)
        print(f"[Archiver] Copied {log_src} to {log_dest}")
    else:
        # Create a mock or write status if log_src doesn't exist yet
        with open(log_dest, "w", encoding="utf-8") as f:
            f.write(
                f"Swarm deploy log archive created at {datetime.now().isoformat()}\n"
            )
        print(f"[Archiver] Created placeholder log at {log_dest}")


if __name__ == "__main__":
    main()
