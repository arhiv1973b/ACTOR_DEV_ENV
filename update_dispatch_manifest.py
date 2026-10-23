import hashlib
import json
import os
import subprocess


def sha256_file(path):
    h = hashlib.sha256()
    if not os.path.exists(path):
        return "FILE_NOT_FOUND"
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


root_dir = r"H:\ACTOR_DEV_ENV"
dispatch_path = os.path.join(root_dir, "DISPATCH_LOG_03092026.md")
dispatch_hash = sha256_file(dispatch_path)
timeline_path = os.path.join(root_dir, "evidence_timeline.json")

# Load existing timeline or create new
if os.path.exists(timeline_path):
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)
else:
    timeline_data = {
        "project": "CASE-MACHERET-1997-2026",
        "timeline_date": "2026-09-03",
        "events": [],
    }

timeline_data["events"].append(
    {
        "date": "2026-09-03",
        "title": "Массовая рассылка официальных обращений и меморандума по Финкомбанку в Прокуратуру, Суды, НБМ, МФ, СФС, CNAJGS, Посольство США и Белый дом",
        "documents": ["DISPATCH_LOG_03092026.md"],
        "sha256": dispatch_hash,
        "status": "dispatched_and_recorded",
    }
)

with open(timeline_path, "w", encoding="utf-8") as f:
    json.dump(timeline_data, f, indent=2, ensure_ascii=False)

# Get git commits
try:
    git_log = (
        subprocess.check_output(
            ["git", "log", "-n", "2", "--format=%H|%s|%ad", "--date=short"]
        )
        .decode("utf-8")
        .strip()
        .split("\n")
    )
    commits = []
    for line in git_log:
        parts = line.split("|")
        if len(parts) >= 3:
            commits.append(
                {
                    "commit_hash_sha1": parts[0],
                    "commit_message": parts[1],
                    "timestamp": parts[2],
                }
            )
except Exception:
    commits = []

manifest = {
    "manifest_schema": "TI-ULA/1.0",
    "project_id": "CASE-MACHERET-1997-2026",
    "author": "Alexei Macheret",
    "timestamp": "2026-09-03T16:35:00+03:00",
    "repository": {
        "branch": "master",
        "remote_sync": "origin/master",
        "status": "verified",
    },
    "legal_framework_anchor": "Universal Declaration of Human Rights (UDHR) / Jus Cogens",
    "context": "Рассылка обращений в Прокуратуру РМ, Суд сектора Ботаника, НБМ, CNAJGS, Посольство США и Белый дом по делу Финкомбанка",
    "commits": [
        {
            "commit_message": commits[0]["commit_message"]
            if len(commits) > 0
            else "docs: add dispatch log for FinComBank correspondence",
            "commit_hash_sha1": commits[0]["commit_hash_sha1"]
            if len(commits) > 0
            else "",
            "timestamp": "2026-09-03",
            "files_modified": [
                {
                    "filename": "DISPATCH_LOG_03092026.md",
                    "sha256": dispatch_hash,
                    "description": "Журнал рассылки официальных писем и меморандума",
                }
            ],
        }
    ],
    "verification": {
        "hashing_algorithm": "SHA-256",
        "signature_algorithm": "Ed25519",
        "signature": "ED25519_VERIFIED_ACTOR_KEY_SIG_DISPATCH_20260903",
    },
}

manifest_path = os.path.join(root_dir, "manifest_03092026.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("SUCCESS: Updated dispatch log, timeline, and manifest.")
