import json
import os


def run_timeline_query():
    print("=== TI-ULA: Recipient Status Timeline CLI Auditor ===")
    # Load recipient status timeline configuration
    config_path = os.path.join(
        os.path.dirname(__file__), "recipient_status_timeline.json"
    )
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print(f"Loaded Query Title: {config['title']}")
        print(f"Visualization Type: {config['visualization']['type']}")

    # Mock data output reflecting CASE-MACHERET-1997-2026 delivery logs
    records = [
        {
            "Recipient": "Суды",
            "Email": "courts@justice.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
            "CheckedAt": 1696410000,
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
            "Recipient": "Министерства",
            "Email": "ministry@justice.md",
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
            "CheckedAt": 1696398000,
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

    for r in sorted(records, key=lambda x: x["CheckedAt"]):
        print(
            f"{r['Recipient']} ({r['Email']}): Sent={r['Sent']} Delivered={r['Delivered']} Acknowledged={r['Acknowledged']} CheckedAt={r['CheckedAt']}"
        )


if __name__ == "__main__":
    run_timeline_query()
