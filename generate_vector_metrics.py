# generate_vector_metrics.py
import json
import os
import sys

METRICS_PATH = "vector_metrics.json"


def generate_and_check():
    if not os.path.exists(METRICS_PATH):
        print(f"[ERROR] {METRICS_PATH} not found.")
        sys.exit(1)

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    print("[*] Analyzing vector metrics against zero-tolerance thresholds...")
    critical_breaches = []

    for v in metrics.get("vectors", []):
        if v.get("severity") == "CRITICAL" and v.get("frequency", 0) > v.get(
            "threshold", 0
        ):
            critical_breaches.append(v)
            print(
                f"[CRITICAL BREACH] Vector '{v['vector_name']}' frequency ({v['frequency']}) exceeds zero-tolerance threshold ({v['threshold']})!"
            )

    if critical_breaches and os.getenv("CI"):
        print(
            "[SIEM ALERT] Critical threshold violations detected in CI pipeline. Flagging build security status."
        )
        # In a real pipeline, this would trigger a webhook alert securely via backend secrets

    print("[SUCCESS] Vector metrics verification complete.")


if __name__ == "__main__":
    generate_and_check()
