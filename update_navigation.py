import os
import glob

nav_html = """
    <nav class="portal-nav" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 2px solid #0c2e4a; margin-bottom: 30px; background-color: #051421; padding: 15px;">
        <div class="breadcrumb">
            <a href="index.html" style="color: #00b8e8; text-decoration: none; font-family: 'Share Tech Mono', monospace;">← PORTAL HUB</a>
        </div>
        <div class="nav-links" style="display: flex; gap: 15px;">
            <a href="timeline.html" class="nav-btn" style="color: #00b8e8; text-decoration: none; padding: 8px 12px; border: 1px solid #00b8e8; border-radius: 4px; font-family: 'Share Tech Mono', monospace; font-size: 0.85em;">⏱️ Chronology</a>
            <a href="EVIDENCE_CATALOG.md" class="nav-btn" style="color: #00b8e8; text-decoration: none; padding: 8px 12px; border: 1px solid #00b8e8; border-radius: 4px; font-family: 'Share Tech Mono', monospace; font-size: 0.85em;">📂 Evidence Catalog</a>
        </div>
    </nav>
"""

# HTML files to process
files = glob.glob("**/*.html", recursive=True)

for file in files:
    # Skip temporary files
    if "gemini-code-" in file:
        continue

    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    # If body tag exists and nav not already present
    if "<body" in content.lower() and '<nav class="portal-nav"' not in content:
        # Find closing bracket of body
        import re

        body_match = re.search(r"<body[^>]*>", content, re.IGNORECASE)
        if body_match:
            end_of_body_tag = body_match.end()
            new_content = (
                content[:end_of_body_tag] + nav_html + content[end_of_body_tag:]
            )

            with open(file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated: {file}")
