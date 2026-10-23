#!/usr/bin/env python3
"""
Link Repair Utility for Apostille Registry & Evidence Portal
Replaces legacy Adobe DocumentCloud / Google Drive viewer links with direct GitHub Pages mirror URLs.
"""

import json
import re
from pathlib import Path


def repair_links():
    print(
        "[*] Starting link repair procedure (DocumentCloud/Google Drive -> GitHub Pages mirror)..."
    )

    # 1. Repair apostilles_registry_90.json
    json_path = Path("H:/ACTOR_DEV_ENV/apostilles_registry_90.json")
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        apostilles = data.get("apostilles", data if isinstance(data, list) else [])
        fixed_count = 0
        for item in apostilles:
            if not isinstance(item, dict):
                continue
            code = item.get("apostille_code")
            sec = item.get("security_code")
            if code and sec:
                expected_url = f"https://arhiv1973b.github.io/apostille-archive-english/apostille_{code}_{sec}.pdf"
                if item.get("download_url") != expected_url:
                    item["download_url"] = expected_url
                    fixed_count += 1
                if item.get("original_url") and "documentcloud.adobe.com" in item.get(
                    "original_url", ""
                ):
                    item["original_url"] = expected_url
                if item.get(
                    "verification_url"
                ) and "documentcloud.adobe.com" in item.get("verification_url", ""):
                    item["verification_url"] = expected_url
                if "recommended_fix" in item and isinstance(
                    item["recommended_fix"], dict
                ):
                    if (
                        "new_url" in item["recommended_fix"]
                        and "documentcloud.adobe.com"
                        in item["recommended_fix"]["new_url"]
                    ):
                        item["recommended_fix"]["new_url"] = expected_url

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] Repaired {fixed_count} download URLs in {json_path}")

    # 2. Repair HTML files referencing old viewer links
    html_files = list(Path("H:/ACTOR_DEV_ENV").glob("*.html")) + list(
        Path("H:/ACTOR_DEV_ENV/apostille-mirror").glob("*.html")
    )
    for hfile in html_files:
        try:
            content = hfile.read_text(encoding="utf-8")
            new_content = re.sub(
                r'https?://(documentcloud\.adobe\.com|drive\.google\.com)[^\s"\'<]+',
                r"https://arhiv1973b.github.io/apostille-archive-english/",
                content,
            )
            if new_content != content:
                hfile.write_text(new_content, encoding="utf-8")
                print(f"[+] Repaired links in HTML file: {hfile}")
        except Exception as e:
            pass

    print("[+] Link repair completed successfully.")


if __name__ == "__main__":
    repair_links()
