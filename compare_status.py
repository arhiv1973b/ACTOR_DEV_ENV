import sys
import os


def compare_status(timeX, timeY, recipient_name):
    print(
        f"Comparing status for recipient '{recipient_name}' between timestamps {timeX} and {timeY}..."
    )

    # Mock records reflecting CASE-MACHERET-1997-2026 delivery logs
    records = [
        {
            "Recipient": "Суды",
            "Email": "courts@justice.md",
            "CheckedAt": 1696410000,
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
        },
        {
            "Recipient": "Суды",
            "Email": "courts@justice.md",
            "CheckedAt": 1696420000,
            "Sent": True,
            "Delivered": True,
            "Acknowledged": True,
        },
        {
            "Recipient": "Прокуратура",
            "Email": "prosecutor@pm.gov.md",
            "CheckedAt": 1696405000,
            "Sent": True,
            "Delivered": True,
            "Acknowledged": True,
        },
        {
            "Recipient": "Министерства",
            "Email": "ministry@justice.md",
            "CheckedAt": 1696398000,
            "Sent": True,
            "Delivered": True,
            "Acknowledged": False,
        },
    ]

    matched = [
        r
        for r in records
        if r["Recipient"] == recipient_name and r["CheckedAt"] in [timeX, timeY]
    ]
    if len(matched) < 2:
        print(
            f"Warning: Found only {len(matched)} status records for {recipient_name} matching timestamps {timeX}, {timeY}. Using available records."
        )
        if len(matched) == 0:
            print("No records found.")
            return

    matched = sorted(matched, key=lambda x: x["CheckedAt"])
    old = matched[0]
    new = matched[-1]

    print(f"\nResult for {old['Recipient']} ({old['Email']}):")
    print(
        f"  Old Timestamp: {old['CheckedAt']} | Sent={old['Sent']}, Delivered={old['Delivered']}, Acknowledged={old['Acknowledged']}"
    )
    print(
        f"  New Timestamp: {new['CheckedAt']} | Sent={new['Sent']}, Delivered={new['Delivered']}, Acknowledged={new['Acknowledged']}"
    )
    print(
        f"  Changes Detected -> SentChanged: {old['Sent'] != new['Sent']}, DeliveredChanged: {old['Delivered'] != new['Delivered']}, AckChanged: {old['Acknowledged'] != new['Acknowledged']}"
    )


if __name__ == "__main__":
    if len(sys.argv) == 4:
        tx, ty, name = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    else:
        # Default test parameters for verification
        tx, ty, name = 1696410000, 1696420000, "Суды"
    compare_status(tx, ty, name)
