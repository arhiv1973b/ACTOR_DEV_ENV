import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
import hashlib

ICLOUD_URL = "https://share.icloud.com/photos/058o77E5I287qz0AVeCiDcimA"


def fetch_icloud_page():
    print(f"[*] Fetching iCloud share page: {ICLOUD_URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(ICLOUD_URL, headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
            # Save raw HTML for inspection
            with open("icloud_page.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("[+] Saved icloud_page.html for inspection.")
        else:
            print(f"[!] Failed to fetch page. Status: {response.status_code}")
    except Exception as e:
        print(f"[!] Error fetching iCloud page: {e}")


if __name__ == "__main__":
    fetch_icloud_page()
