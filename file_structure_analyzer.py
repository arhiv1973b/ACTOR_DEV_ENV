#!/usr/bin/env python3
"""
File Structure & Content Analyzer Script
Сканирует локальный контур, анализирует структуру файлов (JSON, YAML, PDF, TXT),
извлекает метаданные и проверяет целостность (SHA-256).
"""

import os
import json
import yaml
import hashlib

TARGET_DIRS = [r"H:\ACTOR_DEV_ENV", "."]
SUPPORTED_EXTENSIONS = [".json", ".yaml", ".yml", ".txt", ".md"]


def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return "ERROR_READING_FILE"


def analyze_file_structure(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    metrics = {
        "path": filepath,
        "extension": ext,
        "size_bytes": os.path.getsize(filepath),
        "sha256": calculate_sha256(filepath),
        "structure_valid": False,
        "keys_or_lines": 0,
    }

    try:
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                metrics["structure_valid"] = True
                metrics["keys_or_lines"] = (
                    len(data) if isinstance(data, (dict, list)) else 1
                )
        elif ext in [".yaml", ".yml"]:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                metrics["structure_valid"] = True
                metrics["keys_or_lines"] = (
                    len(data) if isinstance(data, (dict, list)) else 1
                )
        elif ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                metrics["structure_valid"] = True
                metrics["keys_or_lines"] = len(lines)
    except Exception as e:
        metrics["parse_error"] = str(e)

    return metrics


def run_analysis():
    print("[*] Запуск глубокого анализа структуры файлов...")
    results = []

    for root_dir in TARGET_DIRS:
        if not os.path.exists(root_dir):
            continue
        for root, dirs, files in os.walk(root_dir):
            if ".git" in root or "node_modules" in root:
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    fpath = os.path.join(root, file)
                    res = analyze_file_structure(fpath)
                    results.append(res)
                    print(
                        f"[+] Проанализирован: {file} (SHA-256: {res['sha256'][:12]}...)"
                    )

    report_path = "file_structure_analysis_report.json"
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(results, rf, ensure_ascii=False, indent=2)
    print(f"[*] Анализ завершен. Отчет сохранен в: {report_path}")


if __name__ == "__main__":
    run_analysis()
