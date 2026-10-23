#!/usr/bin/env python3
"""
Progress Trend Visualizer for MCP Drive Indexer Pipeline
Generates and saves a line chart of Pending vs Completed files over time.
"""

import json
from pathlib import Path
from datetime import datetime

try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend for headless / CI/CD environments
    import matplotlib.pyplot as plt
except ImportError:
    print(
        "Error: matplotlib is not installed. Please install it using 'pip install matplotlib'."
    )
    exit(1)

REPORT_PATH = Path("H:/ACTOR_DEV_ENV/progress_report.json")
OUTPUT_IMAGE = Path("H:/ACTOR_DEV_ENV/progress_trend.png")


def generate_chart():
    if not REPORT_PATH.exists():
        print(f"[-] Report not found: {REPORT_PATH}")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("[-] Report data is empty.")
        return

    timestamps = [datetime.fromisoformat(item["timestamp"]) for item in data]
    pending = [item["pending"] for item in data]
    completed = [item["completed"] for item in data]

    plt.figure(figsize=(10, 6))
    plt.plot(
        timestamps, pending, label="Pending ↓", color="red", marker="o", linewidth=2
    )
    plt.plot(
        timestamps,
        completed,
        label="Completed ↑",
        color="green",
        marker="o",
        linewidth=2,
    )

    plt.title(
        "Pipeline Progress Dynamics: Pending vs Completed",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Timestamp", fontsize=12)
    plt.ylabel("File Count", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=15)
    plt.tight_layout()

    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"[+] Progress trend chart successfully saved to {OUTPUT_IMAGE}")
    plt.close()


if __name__ == "__main__":
    generate_chart()
