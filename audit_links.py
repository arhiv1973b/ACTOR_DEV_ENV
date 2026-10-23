import os
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

EXTENSIONS = (".md", ".json", ".html", ".js")
URL_REGEX = re.compile(r'https?://[^\s\)`"\'<>]+')


def collect_urls():
    urls = set()
    for root, _, files in os.walk("."):
        if any(p in root for p in [".git", ".venv", "node_modules", ".llm_cache"]):
            continue
        for file in files:
            if file.endswith(EXTENSIONS):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        found = URL_REGEX.findall(content)
                        for u in found:
                            if "raw.githubusercontent.com" in u or "github.io" in u:
                                urls.add(u)
                except Exception:
                    pass
    return sorted(list(urls))


def check_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=4) as response:
            return url, response.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception:
        return url, "ERR"


def main():
    urls = collect_urls()
    print(f"Total unique raw/github.io URLs found: {len(urls)}")

    status_counts = {"200": 0, "404": 0, "401/403": 0, "ERR": 0}
    problematic = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            url, code = future.result()
            if code == 200:
                status_counts["200"] += 1
            elif code in (401, 403):
                status_counts["401/403"] += 1
                problematic.append((str(code), url))
            elif code == 404:
                status_counts["404"] += 1
                problematic.append(("404", url))
            else:
                status_counts["ERR"] += 1
                problematic.append(("ERR", url))

    print("\n--- STATISTICS ---")
    for k, v in status_counts.items():
        print(f"{k}: {v}")

    print("\n--- PROBLEMATIC URLS ---")
    for status, url in problematic:
        print(f"{status}  {url}")


if __name__ == "__main__":
    main()
