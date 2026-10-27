import hashlib, json, os, subprocess
from pathlib import Path

# Files to anchor (normalized to first 13 images from archive)
files = [
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_001.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_002.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_003.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_004.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_005.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_006.jpg",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_007.jpg",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_008.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_009.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_010.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_011.jpg",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_012.png",
    r"H:\ACTOR_DEV_ENV\📦 ARCHIVE\Downolde\apostila - 2026-04-24T174117.076_files\Image_013.jpg"
]

def get_hash(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

# Step 1: Hashes
hashes = {Path(f).name: get_hash(f) for f in files}

# Step 2: Merkle Root
def compute_merkle_root(hash_list):
    if len(hash_list) == 1:
        return hash_list[0]
    
    new_level = []
    for i in range(0, len(hash_list), 2):
        if i + 1 < len(hash_list):
            combined = hash_list[i] + hash_list[i+1]
            new_level.append(hashlib.sha256(combined.encode()).hexdigest())
        else:
            new_level.append(hash_list[i])
    return compute_merkle_root(new_level)

merkle_root = compute_merkle_root(list(hashes.values()))

# Step 3: Bundle
bundle = {
    "bundle_id": "BUNDLE-3R-222-26-FINAL",
    "hashes": hashes,
    "merkle_root": merkle_root,
    "timestamp": "2026-06-30T12:35:47+03:00"
}

bundle_path = Path(r"H:\ACTOR_DEV_ENV\apostille-mirror\BUNDLE-3R-222-26-FINAL.json")
bundle_path.parent.mkdir(parents=True, exist_ok=True)
bundle_path.write_text(json.dumps(bundle, indent=2))

print(f"Bundle anchored: {merkle_root}")
