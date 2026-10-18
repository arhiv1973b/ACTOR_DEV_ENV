#!/usr/bin/env python3
"""
Jus Cogens Dossier & Judicial Decision Evaluation Engine
Scans MASTER_DOSSIER/ and evaluates documents against 9 Qubit Vectors (UDHR) & VCLT Arts. 53/64.
Fails build (exit 1) if critical Jus Cogens violations (REJECTED) are detected.
Generates an HTML Dashboard report for GitHub Pages visualization.
"""

import os
import sys
import json
import datetime
from jus_cogens_api import JUS_COGENS_DB

DOSSIER_DIR = "MASTER_DOSSIER"
AUDIT_LOG_PATH = "audit_log.json"
REPORT_JSON_PATH = "jus_cogens_dossier_audit_report.json"
REPORT_HTML_PATH = "jus_cogens_dashboard.html"


def evaluate_content(doc_title, content):
    content_lower = content.lower()
    violations = []
    vectors = JUS_COGENS_DB["qubit_vectors_1_9"]

    if "рабств" in content_lower or "эксплуатац" in content_lower:
        violations.append(
            {
                "vector": "1",
                "name": vectors["1"]["name"],
                "source": vectors["1"]["source"],
            }
        )
    if (
        "пытк" in content_lower
        or "жестокое обращение" in content_lower
        or "бесчеловечн" in content_lower
    ):
        violations.append(
            {
                "vector": "2",
                "name": vectors["2"]["name"],
                "source": vectors["2"]["source"],
            }
        )
    if (
        "дискриминац" in content_lower
        or "расов" in content_lower
        or "по признаку" in content_lower
    ):
        violations.append(
            {
                "vector": "3",
                "name": vectors["3"]["name"],
                "source": vectors["3"]["source"],
            }
        )
    if "произвольное лишение жизни" in content_lower or (
        "смертн" in content_lower and "без суда" in content_lower
    ):
        violations.append(
            {
                "vector": "4",
                "name": vectors["4"]["name"],
                "source": vectors["4"]["source"],
            }
        )
    if "произвольный арест" in content_lower or (
        "задержание" in content_lower and "без закон" in content_lower
    ):
        violations.append(
            {
                "vector": "5",
                "name": vectors["5"]["name"],
                "source": vectors["5"]["source"],
            }
        )
    if (
        "узурпац" in content_lower
        or "лишен права" in content_lower
        or "отказ в иске" in content_lower
    ):
        violations.append(
            {
                "vector": "6",
                "name": vectors["6"]["name"],
                "source": vectors["6"]["source"],
            }
        )
    if (
        "произвольное изъятие" in content_lower
        or "конфискация" in content_lower
        or "заморозк" in content_lower
    ):
        violations.append(
            {
                "vector": "7",
                "name": vectors["7"]["name"],
                "source": vectors["7"]["source"],
            }
        )
    if (
        "свобода мысли" in content_lower
        or "преследование за убеждения" in content_lower
    ):
        violations.append(
            {
                "vector": "8",
                "name": vectors["8"]["name"],
                "source": vectors["8"]["source"],
            }
        )
    if "запрет мирных собраний" in content_lower or "разгон" in content_lower:
        violations.append(
            {
                "vector": "9",
                "name": vectors["9"]["name"],
                "source": vectors["9"]["source"],
            }
        )

    status = "VALID"
    if len(violations) > 0:
        status = "REJECTED_CONDITIONAL" if len(violations) < 3 else "REJECTED"

    return {
        "document": doc_title,
        "status": status,
        "violations_detected": violations,
        "vclt_basis": "Art. 53/64 (Absolute Nullity / Erga Omnes)",
        "actor_recognition": "Individual active standing under Art. 60",
    }


def generate_html_dashboard(report):
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Jus Cogens Dossier Audit Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }}
        h1, h2 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 16px; margin-bottom: 16px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
        th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; }}
        th {{ background: #21262d; color: #8b949e; }}
        .status-valid {{ color: #3fb950; font-weight: bold; }}
        .status-rejected {{ color: #f85149; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>⚖️ Jus Cogens Dossier Audit Dashboard</h1>
    <div class="card">
        <p><strong>Timestamp:</strong> {report["timestamp"]}</p>
        <p><strong>Total Scanned Documents:</strong> {report["total_documents_scanned"]}</p>
        <p><strong>Engine Status:</strong> <span class="status-valid">ACTIVE / SECURE</span></p>
    </div>
    
    <h2>📄 Evaluation Results</h2>
    <table>
        <tr>
            <th>Document</th>
            <th>Status</th>
            <th>VCLT Basis</th>
            <th>Violations Detected</th>
        </tr>
"""
    for ev in report["evaluations"]:
        status_class = "status-valid" if ev["status"] == "VALID" else "status-rejected"
        viol_str = (
            ", ".join([v["name"] for v in ev["violations_detected"]])
            if ev["violations_detected"]
            else "None"
        )
        html_content += f"""        <tr>
            <td>{ev["document"]}</td>
            <td class="{status_class}">{ev["status"]}</td>
            <td>{ev["vclt_basis"]}</td>
            <td>{viol_str}</td>
        </tr>\n"""

    html_content += """    </table>
</body>
</html>
"""
    with open(REPORT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[JUS_COGENS_ENGINE] HTML Dashboard generated at {REPORT_HTML_PATH}")


def run_dossier_audit():
    print(f"[JUS_COGENS_ENGINE] Scanning directory: {DOSSIER_DIR}")
    if not os.path.exists(DOSSIER_DIR):
        print(f"[JUS_COGENS_ENGINE] Directory not found: {DOSSIER_DIR}")
        sys.exit(1)

    results = []
    rejected_count = 0
    for root, _, files in os.walk(DOSSIER_DIR):
        for file in files:
            if (
                file.endswith((".md", ".txt", ".json"))
                and file != "remote_drive_manifest.json"
            ):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    res = evaluate_content(file, content)
                    results.append(res)
                    if res["status"] == "REJECTED":
                        rejected_count += 1
                    print(f" -> Evaluated {file}: Status [{res['status']}]")
                except Exception as e:
                    print(f" -> Error reading {file}: {e}")

    # Ingest remote drive manifest entries
    remote_manifest_path = os.path.join(DOSSIER_DIR, "remote_drive_manifest.json")
    if os.path.exists(remote_manifest_path):
        try:
            with open(remote_manifest_path, "r", encoding="utf-8-sig") as f:
                remote_entries = json.load(f)
            print(
                f"[JUS_COGENS_ENGINE] Ingested {len(remote_entries)} remote drive records from manifest."
            )
            for entry in remote_entries:
                fname = entry.get("FileName", "unknown")
                fpath = entry.get("FullPath", "")
                sha = entry.get("Sha256", "")
                idnp_match = entry.get("IdnpMatch", False)
                variants = entry.get("MatchedVariants", [])
                status_eval = (
                    "VALID"
                    if entry.get("JusCogensStatus") == "VERIFIED_REFERENCE"
                    or not idnp_match
                    else "VALID"
                )

                # Check for violations based on filename/path keywords
                eval_text = f"{fname} {fpath}"
                res = evaluate_content(fname, eval_text)
                res["sha256"] = sha
                res["source_mode"] = "REMOTE_DRIVE_METADATA_ONLY"
                results.append(res)
                if res["status"] == "REJECTED":
                    rejected_count += 1
                print(
                    f" -> Evaluated Remote Drive [SHA:{sha[:8]}...]: {fname} -> Status [{res['status']}]"
                )
        except Exception as e:
            print(f"[JUS_COGENS_ENGINE] Error loading remote drive manifest: {e}")

    report = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_documents_scanned": len(results),
        "evaluations": results,
    }

    with open(REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    generate_html_dashboard(report)

    if rejected_count > 0:
        print(
            f"[JUS_COGENS_ENGINE] CRITICAL: {rejected_count} rejected document(s) detected violating Jus Cogens. Failing build."
        )
        sys.exit(1)
    else:
        print(
            "[JUS_COGENS_ENGINE] All scanned documents passed Jus Cogens verification."
        )


if __name__ == "__main__":
    run_dossier_audit()
