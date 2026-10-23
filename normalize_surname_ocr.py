import os
import re
import json


def normalize_text(text):
    patterns = [
        r"MA\s*qEPET",
        r"МАЧЕРЕТ",
        r"MACHERET",
        r"MACERET",
        r"Мачерет",
        r"Махерет",
    ]
    found = []
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        if matches:
            found.extend(matches)
    return set(found)


def scan_workspace():
    root = r"H:\ACTOR_DEV_ENV"
    results = {}
    allowed_dirs = [
        "MASTER_DOSSIER",
        "evidence",
        "artifacts",
        "Registrul_documentelor_Dosarul_Jus_Cogens_Maceret_si_Oleinik",
    ]

    # Scan root files + allowed dirs
    files_to_scan = []
    for f in os.listdir(root):
        if f.endswith((".md", ".json", ".txt", ".csv")) and os.path.isfile(
            os.path.join(root, f)
        ):
            files_to_scan.append(os.path.join(root, f))

    for ad in allowed_dirs:
        ad_path = os.path.join(root, ad)
        if os.path.exists(ad_path):
            for dp, _, filenames in os.walk(ad_path):
                for f in filenames:
                    if f.endswith((".md", ".json", ".txt", ".csv")):
                        files_to_scan.append(os.path.join(dp, f))

    for fullpath in files_to_scan:
        try:
            with open(fullpath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
                matches = normalize_text(content)
                if matches:
                    rel_name = os.path.relpath(fullpath, root)
                    results[rel_name] = list(matches)
        except Exception:
            pass
    return results


if __name__ == "__main__":
    print("[*] Scanning workspace files for surname OCR variants...")
    res = scan_workspace()
    print(f"[*] Found surname references in {len(res)} files.")
    for fname, variants in res.items():
        print(f"  - {fname}: {variants}")

    output_report = r"H:\ACTOR_DEV_ENV\surname_normalization_report.json"
    with open(output_report, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"[+] Normalization report saved to {output_report}")
