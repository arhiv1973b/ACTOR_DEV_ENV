import hashlib
import os
import json
from datetime import datetime


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


root_dir = r"H:\ACTOR_DEV_ENV"
evidence_dir = os.path.join(root_dir, "🏛️ EVIDENCE", "New_Submissions")

test_files = []
if os.path.exists(evidence_dir):
    for f in os.listdir(evidence_dir):
        if f.endswith(".pdf"):
            test_files.append(os.path.join(evidence_dir, f))

# Also add root files if any
for f in os.listdir(root_dir):
    if f.endswith(".pdf") or f.endswith(".md"):
        test_files.append(os.path.join(root_dir, f))

results = []
for path in test_files[:5]:  # Test first few files
    if os.path.isfile(path):
        file_hash = sha256_file(path)
        stat = os.stat(path)
        creation_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # Test hash renaming technology
        hash_filename = f"{file_hash}.bin"
        hash_path = os.path.join(root_dir, hash_filename)

        # Copy content to hash filename
        with open(path, "rb") as src, open(hash_path, "wb") as dst:
            dst.write(src.read())

        verify_hash = sha256_file(hash_path)
        match = file_hash == verify_hash

        results.append(
            {
                "original_path": os.path.basename(path),
                "sha256": file_hash,
                "hash_filename": hash_filename,
                "snapshot_timestamp": creation_time,
                "hash_verification_passed": match,
            }
        )

        # Clean up test hash file
        if os.path.exists(hash_path):
            os.remove(hash_path)

report = {
    "test_suite": "TI-ULA Raw Hash Invariance & Snapshot Timestamp Test",
    "timestamp": datetime.now().isoformat(),
    "tested_files_count": len(results),
    "results": results,
}

report_path = os.path.join(root_dir, "hash_technology_test_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("SUCCESS: Hash technology test report generated:", report_path)
print(json.dumps(report, indent=2, ensure_ascii=False))
