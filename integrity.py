import hashlib
import os

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_integrity(file_path, expected_hash):
    actual_hash = calculate_sha256(file_path)
    return actual_hash == expected_hash, actual_hash