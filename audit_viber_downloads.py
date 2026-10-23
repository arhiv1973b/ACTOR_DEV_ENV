import os
import datetime

VIBER_DIR = r"C:\Users\arhiv\OneDrive\Документы\ViberDownloads"
OUTPUT_REPORT = r"H:\ACTOR_DEV_ENV\VIBER_DOWNLOADS_FORENSIC_AUDIT.md"


def audit_files():
    if not os.path.exists(VIBER_DIR):
        print(f"Directory not found: {VIBER_DIR}")
        return

    files_data = []
    for f in os.listdir(VIBER_DIR):
        fp = os.path.join(VIBER_DIR, f)
        if os.path.isfile(fp):
            stat = os.stat(fp)
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            ext = os.path.splitext(f)[1].lower()
            files_data.append((stat.st_mtime, mtime, f, ext, size_mb))

    # Sort by modification time (chronological)
    files_data.sort(key=lambda x: x[0])

    report_lines = [
        "# FORENSIC AUDIT & CHRONOLOGICAL TIMELINE: VIBER DOWNLOADS",
        f"**Source Directory:** `{VIBER_DIR}`",
        f"**Audit Timestamp:** {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Total Files Analyzed:** {len(files_data)}",
        "",
        "## Chronological Evidence Matrix (PDF, Video, Audio)",
        "| Modified Timestamp | File Name | Type | Size (MB) | Forensic Significance |",
        "|---|---|---|---|---|",
    ]

    for _, mtime, filename, ext, size in files_data:
        # Determine forensic category based on name and extension
        if ext == ".pdf":
            cat = "Judicial / Legal Submission"
        elif ext in (".mp4", ".m4v"):
            cat = "Video Evidence / Procedural Incident"
        elif ext in (".mp3", ".m4a"):
            cat = "Audio Evidence / Transcripts & Records"
        elif ext in (".jpg", ".png"):
            cat = "Visual Evidence / Artifacts"
        else:
            cat = "General / Binary Artifact"

        report_lines.append(f"| {mtime} | `{filename}` | {ext} | {size} | {cat} |")

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Audit report generated successfully at {OUTPUT_REPORT}")


if __name__ == "__main__":
    audit_files()
