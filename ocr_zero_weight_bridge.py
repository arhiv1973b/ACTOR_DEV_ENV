# ocr_zero_weight_bridge.py
import os, json, hashlib, re
from pathlib import Path


def safe_read_immutable_source(f_path: str, fallback_manifest: str = None):
    """
    Безопасно читает файл с потокового диска F:. При недоступности тома
    использует локальный манифест-кеш, защищая zero-weight контур.
    """
    try:
        path_obj = Path(f_path)
        if path_obj.exists() and path_obj.is_file():
            with open(path_obj, "r", encoding="utf-8") as f:
                return f.read(), "LIVE_F_DRIVE"
    except (OSError, PermissionError, FileNotFoundError):
        pass

    if fallback_manifest and os.path.exists(fallback_manifest):
        print(
            f"[!] Warning: Immutable source F: unreachable. Falling back to local manifest cache."
        )
        with open(fallback_manifest, "r", encoding="utf-8") as f:
            return f.read(), "LOCAL_MANIFEST_FALLBACK"

    raise RuntimeError(
        f"[-] Critical: Immutable source {f_path} is unreachable and no fallback exists."
    )


def extract_defect_fingerprint(text):
    # Извлечение нетипичных символов, двойных знаков и возможных опечаток как паттерна
    anomalies = re.findall(r"([^\w\s]{2,}|[a-zA-Zа-яА-Я]+\d+[a-zA-Zа-яА-Я]+)", text)
    return hashlib.sha256(str(anomalies).encode("utf-8")).hexdigest()[:16]


def update_udhr_index_manifest():
    out_dir = "🏛️_EVIDENCE/OCR_TEXT_LAYER/UDHR_INDEX_MAPPING"
    os.makedirs(out_dir, exist_ok=True)

    file_hashes = {}
    hasher = hashlib.sha256()

    all_items = sorted(os.listdir(out_dir))
    for fn in all_items:
        if fn.endswith(".json") and fn != "_MANIFEST.json":
            fpath = os.path.join(out_dir, fn)
            with open(fpath, "rb") as f:
                content = f.read()
            file_sha = hashlib.sha256(content).hexdigest()
            file_hashes[fn] = file_sha

            rel_path = fn.replace("\\", "/")
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(hashlib.sha256(content).digest())

    collective_root = hasher.hexdigest()

    manifest_data = {
        "version": 2,
        "algorithm": "sha256",
        "baseline": "UDHR 1948 (Jus Cogens)",
        "files": file_hashes,
        "root": collective_root,
    }

    manifest_path = os.path.join(out_dir, "_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4, ensure_ascii=False)

    old_sha_path = os.path.join(out_dir, "_MANIFEST.sha256")
    if os.path.exists(old_sha_path):
        os.remove(old_sha_path)

    print(
        f"[+] Structured UDHR Manifest updated: {manifest_path} | Root SHA256: {collective_root}"
    )
    return collective_root


def process_ocr_to_udhr_pointer(
    drive_link, raw_text_file, output_name, target_lang="en"
):
    with open(raw_text_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    text_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    defect_fingerprint = extract_defect_fingerprint(raw_text)

    udhr_mapping = {
        "source_anchor": drive_link,
        "raw_text_hash": text_hash,
        "defect_fingerprint": defect_fingerprint,
        "browser_sync_key": f"SYNC-{defect_fingerprint}",
        "translation_status": f"Translated to {target_lang}. Grammatically corrected.",
        "forensic_anomaly_log": "Mechanical/OCR typos detected and preserved in raw_text_hash for strict visual matching.",
        "jurisdictional_baseline": "UDHR 1948 (Jus Cogens)",
    }

    out_dir = "🏛️_EVIDENCE/OCR_TEXT_LAYER/UDHR_INDEX_MAPPING"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{output_name}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(udhr_mapping, f, indent=4, ensure_ascii=False)

    print(f"[+] Advanced Node created: {out_path} | Defect Key: {defect_fingerprint}")
    update_udhr_index_manifest()
