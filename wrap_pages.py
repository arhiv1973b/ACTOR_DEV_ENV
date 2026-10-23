import pathlib
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "base.html"

def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding='utf-8')

def extract_body(html: str) -> str:
    # Try to extract everything inside <body> tags; if not found, return whole html
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else html.strip()

def wrap_file(html_path: Path) -> None:
    original = html_path.read_text(encoding='utf-8')
    # Get title if present
    title_match = re.search(r'<title>(.*?)</title>', original, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ''
    body_content = extract_body(original)
    template = load_template()
    rendered = template.replace('{{ title }}', title).replace('{{ content }}', body_content)
    # Optionally add current year placeholder
    rendered = rendered.replace('{{ year }}', str(Path().resolve().stat().st_mtime))
    html_path.write_text(rendered, encoding='utf-8')
    print(f"[Wrap] Wrapped {html_path}")

def main():
    for html_path in BASE_DIR.rglob('*.html'):
        # Skip the base template itself
        if html_path.samefile(TEMPLATE_PATH):
            continue
        wrap_file(html_path)

if __name__ == '__main__':
    main()
