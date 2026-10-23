import urllib.request
import urllib.error

TARGET_URLS = [
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/JUS_COGENS_ERGA_OMNES_MASTER_SYNTHESIS.md",
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/FORENSIC_FINCOM_ANALYSIS.md",
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/IDENTITY_DISTORTION_GRAPH.md",
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/LEGAL_MEMORANDUM_ECHR.md",
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/ROOT_MANIFEST_2026.md",
    "https://raw.githubusercontent.com/arhiv1973b/apostille-mirror/master/ti_ula_crypto_manifest.json",
]


def check_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as res:
            return res.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return "ERR/TIMEOUT"


def main():
    print("=== TARGETED TUNNEL LINK AUDIT (DOCUMENT SYNCHRONIZATION) ===")
    for url in TARGET_URLS:
        code = check_url(url)
        print(f"[{code}] {url}")


if __name__ == "__main__":
    main()
