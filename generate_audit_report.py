import datetime
import subprocess
import os


def generate_report():
    print("Generating Delivery Status Audit Report...")
    records = [
        {
            "Recipient": "Министерства",
            "Email": "ministry@justice.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
            "CheckedAt": 1696398000,
        },
        {
            "Recipient": "Прокуратура",
            "Email": "prosecutor@pm.gov.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": True,
            "CheckedAt": 1696405000,
        },
        {
            "Recipient": "Суды",
            "Email": "courts@justice.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
            "CheckedAt": 1696410000,
        },
        {
            "Recipient": "Финансовые регуляторы",
            "Email": "secretariat@bnm.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
            "CheckedAt": 1696412000,
        },
        {
            "Recipient": "Международные миссии",
            "Email": "ohchr-petitions@un.org",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": True,
            "CheckedAt": 1696415000,
        },
    ]

    lines = [
        "# Delivery Status Audit Report",
        f"**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "**Case:** CASE-MACHERET-1997-2026 (TI-ULA / A©tor Protocol)",
        "",
        "| Recipient | Email | Sent | Delivered | Acknowledged | CheckedAt |",
        "|-----------|-------|------|-----------|--------------|-----------|",
    ]

    for r in sorted(records, key=lambda x: x["CheckedAt"]):
        lines.append(
            f"| {r['Recipient']} | {r['Email']} | {r['Sent']} | {r['Delivered']} | {r['Acknowledged']} | {r['CheckedAt']} |"
        )

    report_path = os.path.join(os.path.dirname(__file__), "DeliveryStatus_Audit.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Report written to {report_path}")

    # Git operations
    subprocess.run(["git", "add", "DeliveryStatus_Audit.md"], check=True)
    commit_msg = f"Audit report update: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(
        ["git", "push", "origin", "feature/cyber-sabotage-audit-10-2026"], check=True
    )
    print("Audit report committed and pushed successfully.")


if __name__ == "__main__":
    generate_report()
