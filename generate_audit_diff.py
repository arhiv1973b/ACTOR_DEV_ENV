import datetime
import difflib
import os
import subprocess
import shutil


def generate_diff():
    print("Generating Delivery Status Audit Diff Report...")
    old_file = "DeliveryStatus_Audit_prev.md"
    new_file = "DeliveryStatus_Audit.md"
    diff_file = "DeliveryStatus_Audit_Diff.md"

    # Ensure files exist
    if not os.path.exists(new_file):
        print(f"Error: {new_file} does not exist.")
        return

    if not os.path.exists(old_file):
        # Create a baseline prev file if none exists
        shutil.copy(new_file, old_file)
        print(f"Created baseline {old_file} from {new_file}")

    with (
        open(old_file, "r", encoding="utf-8") as f1,
        open(new_file, "r", encoding="utf-8") as f2,
    ):
        old_lines = f1.readlines()
        new_lines = f2.readlines()

    diff = difflib.unified_diff(
        old_lines, new_lines, fromfile=old_file, tofile=new_file, lineterm=""
    )

    diff_table_lines = [
        "# Delivery Status Audit Diff Report",
        f"**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        "| ChangeType | Line |",
        "|------------|------|",
    ]

    has_changes = False
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            diff_table_lines.append(f"| Added | {line[1:].strip()} |")
            has_changes = True
        elif line.startswith("-") and not line.startswith("---"):
            diff_table_lines.append(f"| Removed | {line[1:].strip()} |")
            has_changes = True

    if not has_changes:
        diff_table_lines.append("| No Changes | Baseline matches current state |")

    with open(diff_file, "w", encoding="utf-8") as f:
        f.write("\n".join(diff_table_lines) + "\n")
    print(f"Diff report written to {diff_file}")

    # Git operations
    subprocess.run(["git", "add", diff_file], check=True)
    commit_msg = f"Audit diff report update: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    subprocess.run(
        ["git", "push", "origin", "feature/cyber-sabotage-audit-10-2026"], check=True
    )
    print("Audit diff report committed and pushed successfully.")


if __name__ == "__main__":
    generate_diff()
