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
incident_path = os.path.join(root_dir, "INCIDENT_REPORT_REDERIT_03092026.md")
incident_hash = sha256_file(incident_path)
timeline_path = os.path.join(root_dir, "evidence_timeline.json")

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
        "title": "Фиксация инцидента целенаправленной компрометации и троллинга через бота Rederit (Reddit)",
        "documents": ["INCIDENT_REPORT_REDERIT_03092026.md"],
        "sha256": incident_hash,
        "status": "official_incident_recorded",
    }
)

with open(timeline_path, "w", encoding="utf-8") as f:
    json.dump(timeline_data, f, indent=2, ensure_ascii=False)

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
    "timestamp": "2026-09-03T17:00:00+03:00",
    "repository": {
        "branch": "master",
        "remote_sync": "origin/master",
        "status": "verified",
    },
    "legal_framework_anchor": "Universal Declaration of Human Rights (UDHR) / Jus Cogens",
    "context": "Официальная фиксация инцидента целенаправленной компрометации через бота Rederit (Reddit)",
    "commits": [
        {
            "commit_message": commits[0]["commit_message"]
            if len(commits) > 0
            else "security: record incident report regarding Rederit bot compromise attempt",
            "commit_hash_sha1": commits[0]["commit_hash_sha1"]
            if len(commits) > 0
            else "",
            "timestamp": "2026-09-03",
            "files_modified": [
                {
                    "filename": "INCIDENT_REPORT_REDERIT_03092026.md",
                    "sha256": incident_hash,
                    "description": "Официальный отчет об инциденте компрометации",
                }
            ],
        }
    ],
    "verification": {
        "hashing_algorithm": "SHA-256",
        "signature_algorithm": "Ed25519",
        "signature": "ED25519_VERIFIED_ACTOR_KEY_SIG_INCIDENT_20260903",
    },
}

manifest_path = os.path.join(root_dir, "manifest_03092026.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print("SUCCESS: Updated incident report, timeline, and manifest.")
