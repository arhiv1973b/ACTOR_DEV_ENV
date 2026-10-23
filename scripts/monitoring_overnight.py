#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitoring_overnight.py

Lightweight monitoring script (HEAD by default) with exponential backoff,
optional OG check (GET), and JSON reports. Designed to run locally or inside
CI (manual dispatch).

Usage:
  pip3 install requests
  python3 scripts/monitoring_overnight.py scripts/urls.txt --check-og --max-retries 3

Outputs:
  - report_link_results.json  (array of results)
  - alerts.json              (array of alerts, if any)

Preserves protected tokens: ©, A©tor, Jus Cogens, Erga Omnes, Alexei Macheret, TI-ULA

"""

import argparse
import requests
import json
import time
import logging
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def perform_request(url, method='HEAD', max_retries=3):
    backoff_times = [5, 20, 60]

    for attempt in range(max_retries + 1):
        try:
            start_time = time.time()
            if method == 'HEAD':
                response = requests.head(url, allow_redirects=True, timeout=10)
            else:
                response = requests.get(url, allow_redirects=True, timeout=10)
            latency = int((time.time() - start_time) * 1000)

            # Если 4xx или 5xx, обрабатываем как ошибку
            if response.status_code >= 400:
                raise requests.exceptions.HTTPError(f"HTTP {response.status_code}", response=response)

            return {
                "status": "ok",
                "code": response.status_code,
                "latency_ms": latency,
                "text": response.text if method == 'GET' else None,
                "headers": dict(response.headers)
            }

        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            # extract possible status code
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    status_code = e.response.status_code
                except Exception:
                    status_code = None

            if attempt < max_retries:
                sleep_time = backoff_times[attempt] if attempt < len(backoff_times) else 60
                logging.warning(f"URL: {url} | Error: {e} | Retry in {sleep_time}s (Attempt {attempt + 1}/{max_retries})")
                time.sleep(sleep_time)
            else:
                return {
                    "status": "error",
                    "code": status_code,
                    "error": str(e)
                }


def main():
    parser = argparse.ArgumentParser(description="Overnight Monitoring Script")
    parser.add_argument("urls_file", help="Файл со списком URL")
    parser.add_argument("--check-og", action="store_true", help="Включить проверку OG-тегов (GET запрос)")
    parser.add_argument("--max-retries", type=int, default=3, help="Максимальное число повторов")
    args = parser.parse_args()

    if not os.path.exists(args.urls_file):
        logging.error(f"File {args.urls_file} not found.")
        return

    with open(args.urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    results = []
    alerts = []

    for url in urls:
        logging.info(f"Checking: {url}")

        # choose method
        method = 'GET' if args.check_og else 'HEAD'
        res = perform_request(url, method=method, max_retries=args.max_retries)

        report_item = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "url": url,
            "status": "ok" if res.get("status") == "ok" else "error",
            "code": res.get("code"),
            "latency_ms": res.get("latency_ms", 0),
            "og_ok": None,
            "error_message": res.get("error", "")
        }

        # escalation on error
        if report_item["status"] == "error":
            alert = {
                "subject": f"[ALERT] URL DOWN {report_item['code']} {url}",
                "body": f"Timestamp: {report_item['timestamp']}\nLast Error: {report_item['error_message']}"
            }
            alerts.append(alert)
            logging.error(f"CRITICAL DOWN: {url}")

        # OG check
        elif args.check_og and res.get("text"):
            html_lower = res["text"].lower()
            if 'property="og:title"' in html_lower and 'property="og:description"' in html_lower:
                report_item["og_ok"] = True
            else:
                report_item["og_ok"] = False
                alerts.append({
                    "subject": f"[WARN] OG missing: {url}",
                    "body": "Meta tags absent. Action: confirm OG injected in build pipeline."
                })
                logging.warning(f"OG MISSING: {url}")

        results.append(report_item)
        # polite delay
        time.sleep(1)

    # write outputs
    with open("report_link_results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    if alerts:
        with open("alerts.json", "w", encoding='utf-8') as f:
            json.dump(alerts, f, ensure_ascii=False, indent=4)
        logging.info(f"Saved {len(alerts)} alerts to alerts.json")

    logging.info("Monitoring run complete. Outputs: report_link_results.json, alerts.json (if any)")


if __name__ == "__main__":
    main()
