import os
import hashlib
from pathlib import Path


def generate_sha256_checksums(output_path="05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines = []
    root_dir = Path(".")

    for path in sorted(root_dir.glob("*")):
        if path.is_file() and path.name != "generate_checksums.py":
            path_str = str(path).replace("\\", "/")
            h = hashlib.sha256()
            try:
                with open(path, "rb") as f:
                    for chunk in iter(lambda: f.read(65536), b""):
                        h.update(chunk)
                sha = h.hexdigest()
                lines.append(f"{sha}  {path_str}")
            except Exception as e:
                print(f"Error reading {path}: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(
        f"SHA-256 checksums successfully written to {output_path} ({len(lines)} files hashed)."
    )


if __name__ == "__main__":
    generate_sha256_checksums()
