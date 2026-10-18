#!/usr/bin/env python3
"""
Progress Trend Chart Generator (Matplotlib)
Reads progress_report.json and generates progress_trend.png
"""

import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

def generate_png_chart(json_path="progress_report.json", output_png="progress_trend.png"):
    path = Path(json_path)
    if not path.exists():
        print(f"Error: {json_path} not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("No data points found in report.")
        return

    timestamps = []
    pending = []
    completed = []

    for item in data:
        ts_str = item.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts_str.replace("Z", ""))
        except:
            dt = datetime.now()
        timestamps.append(dt)
        pending.append(item.get("pending", 0))
        completed.append(item.get("completed", 0))

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, pending, label="Pending ↓", color="#da3633", marker="o", linewidth=2.5)
    plt.plot(timestamps, completed, label="Completed ↑", color="#238636", marker="s", linewidth=2.5)

    plt.title("Pipeline Progress Dynamics: Pending vs Completed", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Timestamp", fontsize=12)
    plt.ylabel("File Count", fontsize=12)
    plt.legend(fontsize=12, loc="center right")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    out_file = Path(output_png)
    plt.savefig(out_file, dpi=300)
    plt.close()
    print(f"PNG trend chart successfully saved to: {out_file.absolute()}")

if __name__ == "__main__":
    generate_png_chart()
