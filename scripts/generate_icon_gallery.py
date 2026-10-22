#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate an HTML gallery of folder icons from vscode-icons VSIX archive.
"""

import zipfile
import os
from pathlib import Path
from datetime import datetime

vsix_path = Path(r"C:\Users\arhiv\Downloads\Downolde\vscode-icons-13.0.0.vsix")
extract_dir = Path(r"H:\ACTOR_DEV_ENV\folder_icons_svg")
gallery_path = Path(r"H:\ACTOR_DEV_ENV\reports\folder_icons_gallery.html")

extract_dir.mkdir(parents=True, exist_ok=True)
gallery_path.parent.mkdir(parents=True, exist_ok=True)

icons = []

print("[*] Extracting folder icons from VSIX...")
with zipfile.ZipFile(vsix_path, 'r') as z:
    for file in z.namelist():
        if file.startswith("extension/icons/folder_type_") and file.endswith(".svg"):
            file_name = Path(file).name
            target = extract_dir / file_name
            with z.open(file) as src, open(target, "wb") as dst:
                content = src.read()
                dst.write(content)
            icons.append((file_name, content.decode("utf-8", errors="ignore")))

print(f"[+] Extracted {len(icons)} icons to {extract_dir}")

print("[*] Generating HTML gallery...")
html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VS Code Folder Icons Gallery — A©tor Navigator</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            margin: 0;
            padding: 30px;
        }}
        h1 {{
            color: #f0f6fc;
            border-bottom: 1px solid #30363d;
            padding-bottom: 15px;
        }}
        .search-box {{
            margin: 20px 0;
            padding: 10px 15px;
            width: 100%;
            max-width: 400px;
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            font-size: 16px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 15px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .card:hover {{
            transform: translateY(-3px);
            border-color: #58a6ff;
        }}
        .icon-container {{
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }}
        .icon-container svg {{
            max-width: 100%;
            max-height: 100%;
        }}
        .name {{
            font-size: 12px;
            font-family: monospace;
            color: #8b949e;
            word-break: break-all;
        }}
        footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #8b949e;
            border-top: 1px solid #30363d;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>📁 VS Code Folder Icons Gallery</h1>
    <p>Коллекция иконок папок из пакета <code>vscode-icons</code> (всего: {len(icons)}).</p>
    <input type="text" id="search" class="search-box" placeholder="Поиск иконки по имени..." onkeyup="filterIcons()">
    
    <div class="grid" id="iconGrid">
"""

for name, svg_content in sorted(icons):
    html += f"""
        <div class="card" data-name="{name.lower()}">
            <div class="icon-container">{svg_content}</div>
            <div class="name">{name}</div>
        </div>
    """

html += f"""
    </div>

    <script>
        function filterIcons() {{
            const input = document.getElementById('search').value.toLowerCase();
            const cards = document.getElementsByClassName('card');
            for (let i = 0; i < cards.length; i++) {{
                const name = cards[i].getAttribute('data-name');
                if (name.includes(input)) {{
                    cards[i].style.display = "";
                }} else {{
                    cards[i].style.display = "none";
                }}
            }}
        }}
    </script>
    <footer>
        A©tor Navigator &bull; Forensic & UI Asset Pipeline &bull; Generated {datetime.now().isoformat()}
    </footer>
</body>
</html>
"""

with open(gallery_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[+] HTML gallery generated successfully at: {gallery_path}")
