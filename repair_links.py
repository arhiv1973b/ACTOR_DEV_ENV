import pathlib
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "base.html"

def load_template() -> str:
    return TEMPLATE_PATH.read_text(encoding='utf-8')

def replace_content(html_path: Path, new_body: str) -> None:
    # Simple replacement: replace the whole <body>...</body> with new_body wrapped by template
    content = html_path.read_text(encoding='utf-8')
    # Extract original title if present
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else ""
    # Build rendered page
    template = load_template()
    rendered = template.replace('{{ title }}', title).replace('{{ content }}', new_body)
    # Write back
    html_path.write_text(rendered, encoding='utf-8')

def repair_internal_links(broken_items):
    # broken_items is list of dicts from audit_links JSON output
    for item in broken_items:
        file_path = BASE_DIR / item['file']
        line_no = item['line']
        href = item['href']
        # Try to locate a file with a similar name in the project
        candidate = None
        name = Path(href).name
        for p in BASE_DIR.rglob(name):
            candidate = p
            break
        if candidate:
            # Compute relative path from html file
            rel = os.path.relpath(candidate, start=file_path.parent)
            # Replace the href in the file (single occurrence on the line)
            text = file_path.read_text(encoding='utf-8')
            lines = text.splitlines()
            target_line = lines[line_no-1]
            new_line = target_line.replace(href, rel)
            lines[line_no-1] = new_line
            file_path.write_text('\n'.join(lines), encoding='utf-8')
            print(f"[Repair] Fixed {file_path} line {line_no}: {href} -> {rel}")
        else:
            print(f"[Repair] No candidate found for {href} in {file_path}")

if __name__ == '__main__':
    # Expect JSON from audit_links printed to stdout
    data = json.load(sys.stdin)
    broken_internal = data.get('broken_internal', [])
    repair_internal_links(broken_internal)
