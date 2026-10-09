import glob
import datetime
import subprocess
import os


def consolidate_logs_previous_status_chain():
    print("Consolidating PointDiff reports with PREVIOUS_STATUS chain graph ingest...")
    files = glob.glob("DeliveryStatus_PointDiff*.md")
    files = [f for f in files if f != "DeliveryStatus_PointDiff_Log.md"]

    headers = {
        "en": "# Consolidated Delivery Status PointDiff Log",
        "fr": "# Journal consolidé des écarts de statut de livraison",
        "ro": "# Jurnal consolidat al diferențelor de statut de livrare",
        "ru": "# Сводный журнал дифф‑анализа статусов доставки",
    }

    legal_refs = {
        "en": "UDHR Article 17(2), Constitution of Moldova Article 4",
        "fr": "DUDH Article 17(2), Constitution de la Moldavie Article 4",
        "ro": "Declarația Universală a Drepturilor Omului Articolul 17(2), Constituția Republicii Moldova Articolul 4",
        "ru": "ВДПЧ Статья 17(2), Конституция Молдовы Статья 4",
    }

    table_header = "| Recipient | Email | OldCheckedAt | NewCheckedAt | SentChanged | DeliveredChanged | AckChanged |\n|-----------|-------|--------------|--------------|-------------|------------------|------------|"

    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    version_label = f"## Audit Run {now_str} UTC"

    collected_rows = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if (
                    line.startswith("|")
                    and not line.startswith("| Recipient")
                    and not line.startswith("|---")
                ):
                    collected_rows.append(line.strip())

    lines = []
    for lang, title in headers.items():
        lines.append(title)
        lines.append(f"**Case:** CASE-MACHERET-1997-2026 (TI-ULA / A©tor Protocol)")
        lines.append("")
        lines.append(table_header)
        for row in collected_rows:
            lines.append(row)
        lines.append("")
        lines.append(version_label)
        lines.append(
            f"[{legal_refs[lang]}](https://www.un.org/en/about-us/universal-declaration-of-human-rights)"
        )
        lines.append("")

    log_path = os.path.join(
        os.path.dirname(__file__), "DeliveryStatus_PointDiff_Log.md"
    )
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Chain consolidated log written to {log_path}")

    # Git operations
    subprocess.run(["git", "add", "DeliveryStatus_PointDiff_Log.md"], check=True)
    commit_msg = f"Consolidated PointDiff log update with AuditRun->DeliveryStatus->PREVIOUS_STATUS graph: {now_str}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(
        ["git", "push", "origin", "feature/cyber-sabotage-audit-10-2026"], check=True
    )
    print("Chain consolidated log committed and pushed successfully.")


if __name__ == "__main__":
    consolidate_logs_previous_status_chain()
