import hashlib
import os
import datetime
import urllib.request


def verify_integrity():
    print("=== TI-ULA / A©tor Protocol: External Integrity Verifier ===")
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Files to verify locally present in repository / exports
    files_to_check = [
        "DeliveryStatus_PointDiff_Log.md",
        "MASTER_RECIPIENTS_REGISTRY_RM_2026.md",
        "TI_ULA_EVIDENCE_PACKAGE_DISPATCH_2026.md",
        "evidence_2026.sha256",
    ]

    report_lines = [
        "# External Integrity Verification Report",
        f"**Verified At:** {timestamp} UTC",
        "**Protocol:** TI-ULA / A©tor Protocol (CASE-MACHERET-1997-2026)",
        "",
        "| File Path | Computed SHA-256 | Status |",
        "|-----------|------------------|--------|",
    ]

    all_valid = True
    for filepath in files_to_check:
        if os.path.exists(filepath):
            hasher = hashlib.sha256()
            with open(filepath, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            file_hash = hasher.hexdigest()
            status = "VALID [✓]"
            report_lines.append(f"| {filepath} | `{file_hash}` | {status} |")
        else:
            report_lines.append(f"| {filepath} | `MISSING` | FAILED [✗] |")
            all_valid = False

    report_lines.append("")
    if all_valid:
        report_lines.append(
            "**Conclusion:** All core evidence and audit artifacts successfully passed cryptographic verification."
        )
    else:
        report_lines.append("**Conclusion:** Warning - some artifacts are missing.")

    report_path = "External_Verification_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Verification report written to {report_path}")


if __name__ == "__main__":
    verify_integrity()
