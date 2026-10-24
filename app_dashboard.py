#!/usr/bin/env python3
"""
CASE-MACHERET Forensic Dashboard & Correlation Portal
IDNP: 2000001159655
Direct Access to F:\\Мой диск\\ without duplication or moving.
Integrated GitHub SSH Authentication & Correlation Norms.
"""

import os
import subprocess
from flask import Flask, render_template_string, send_file, abort

app = Flask(__name__)

# Core Artifacts in workspace
ARTIFACTS = {
    "svg_graph": r"H:\ACTOR_DEV_ENV\03_GRAPH_GRAPHICS\signature_evidence_graph.svg",
    "dot_graph": r"H:\ACTOR_DEV_ENV\03_GRAPH_GRAPHICS\audit_graph_full.dot",
    "manifest": r"H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\ACTOR_MANIFEST_SIGNATURE.json",
    "checksums": r"H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\CHECKSUMS_SHA256.txt",
    "pubkey": r"H:\ACTOR_DEV_ENV\05_CRYPTO_MANIFESTS\GPG_PUBLIC_KEY.asc",
}

# Scan F:\Мой диск for case files without moving/duplicating
F_DRIVE_ROOT = r"F:\Мой диск"
case_files = {}

if os.path.exists(F_DRIVE_ROOT):
    for root, dirs, files in os.walk(F_DRIVE_ROOT):
        for f in files:
            if f.lower().endswith(('.pdf', '.docx', '.doc', '.txt')) and any(kw in f.lower() for kw in ['mach', 'reviz', 'demers', 'sesiz', 'galina', 'cerere', 'scrisoare', 'statut']):
                rel_name = os.path.relpath(os.path.join(root, f), F_DRIVE_ROOT)
                case_files[rel_name] = os.path.join(root, f)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>CASE-MACHERET | Forensic Correlation Portal</title>
    <style>
        body { font-family: monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
        header { border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 20px; }
        h1 { color: #58a6ff; font-size: 1.5em; }
        .badge { background: #238636; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; }
        .section { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 15px; margin-bottom: 20px; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 8px 0; }
        a { color: #58a6ff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .meta { color: #8b949e; font-size: 0.9em; }
    </style>
</head>
<body>
    <header>
        <h1>CASE-MACHERET FORENSIC CORRELATION PORTAL</h1>
        <div class="meta">Subject IDNP: <strong>2000001159655</strong> | Name: <strong>Macheret</strong> | GitHub SSH: <span class="badge">{{ ssh_status }}</span></div>
    </header>

    <div class="section">
        <h2>1. Core Forensic Artifacts</h2>
        <ul>
            {% for key, path in artifacts.items() %}
            <li>🔗 <a href="/artifact/{{ key }}" target="_blank">{{ key }}</a> <span class="meta">({{ path }})</span></li>
            {% endfor %}
        </ul>
    </div>

    <div class="section">
        <h2>2. Direct F:\\Мой диск Files (Zero Duplication / Zero Movement)</h2>
        <ul>
            {% for rel_name, full_path in case_files.items() %}
            <li>📄 <a href="/fdrive?path={{ rel_name }}" target="_blank">{{ rel_name }}</a> <span class="meta">({{ full_path }})</span></li>
            {% endfor %}
        </ul>
    </div>

    <div class="section">
        <h2>3. Imperative Compliance & Norms</h2>
        <p>Absolute transparency enforced. Zero pseudonymization. Direct binding to IDNP 2000001159655. UDHR standards applied.</p>
    </div>
</body>
</html>
"""

def check_github_ssh():
    try:
        res = subprocess.run(["ssh", "-T", "git@github.com"], capture_output=True, text=True, timeout=5)
        return res.stdout.strip() or res.stderr.strip()
    except Exception as e:
        return f"SSH Error: {e}"

@app.route("/")
def index():
    ssh_out = check_github_ssh()
    return render_template_string(HTML_TEMPLATE, artifacts=ARTIFACTS, case_files=case_files, ssh_status=ssh_out)

@app.route("/artifact/<name>")
def get_artifact(name):
    if name in ARTIFACTS and os.path.exists(ARTIFACTS[name]):
        return send_file(ARTIFACTS[name])
    abort(404)

@app.route("/fdrive")
def get_fdrive():
    from flask import request
    rel_path = request.args.get('path')
    if rel_path and rel_path in case_files:
        full_path = case_files[rel_path]
        if os.path.exists(full_path):
            return send_file(full_path)
    abort(404)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
"""
filePath: H:\ACTOR_DEV_ENV\app_dashboard.py
