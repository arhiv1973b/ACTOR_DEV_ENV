import os
import re
import sys
import json
import pathlib
import requests
from datetime import datetime

BASE_DIR = pathlib.Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "audit_reports"
REPORTS_DIR.mkdir(exist_ok=True)

HTML_GLOB = "**/*.html"

def is_external(url: str) -> bool:
    return url.startswith('http://') or url.startswith('https://') or url.startswith('//')

def check_external(url: str) -> bool:
    try:
        if url.startswith('//'):
            url = 'https:' + url
        resp = requests.head(url, timeout=5, allow_redirects=True)
        return resp.status_code < 400
    except Exception:
        return False

def resolve_internal(base_path: pathlib.Path, href: str) -> pathlib.Path:
    href = href.split('#')[0].split('?')[0]
    tgt = (base_path.parent / href).resolve()
    return tgt

def audit_html_file(html_path: pathlib.Path):
    broken_ext = []
    broken_int = []
    content = html_path.read_text(encoding='utf-8')
    for i, line in enumerate(content.splitlines(), start=1):
        for match in re.finditer(r'href\s*=\s*"([^"]+)"', line, re.IGNORECASE):
            url = match.group(1).strip()
            if is_external(url):
                if not check_external(url):
                    broken_ext.append((i, url))
            else:
                tgt = resolve_internal(html_path, url)
                if not tgt.exists():
                    broken_int.append((i, url, str(tgt)))
    return broken_ext, broken_int

def generate_report(all_broken_ext, all_broken_int):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = REPORTS_DIR / f"audit_{timestamp}.md"
    with report_path.open('w', encoding='utf-8') as f:
        f.write(f"# Audit Report – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write('## Битые внешние ссылки\n')
        f.write('| Файл | Строка | Ссылка |\n|------|--------|--------|\n')
        for file, line, url in all_broken_ext:
            f.write(f"| {file} | {line} | {url} |\n")
        f.write('\n## Битые внутренние ссылки\n')
        f.write('| Файл | Строка | Ссылка | Ожидаемый путь |\n|------|--------|--------|----------------|\n')
        for file, line, url, expect in all_broken_int:
            f.write(f"| {file} | {line} | {url} | {expect} |\n")
    return report_path

def main():
    all_broken_ext = []
    all_broken_int = []
    for html_path in BASE_DIR.glob(HTML_GLOB):
        if html_path.is_file():
            be, bi = audit_html_file(html_path)
            if be:
                for line, url in be:
                    all_broken_ext.append((html_path.relative_to(BASE_DIR), line, url))
            if bi:
                for line, url, expect in bi:
                    all_broken_int.append((html_path.relative_to(BASE_DIR), line, url, expect))
    report = generate_report(all_broken_ext, all_broken_int)
    print(f"[Audit] Report generated: {report}")
    result = {
        "report": str(report),
        "broken_internal": [
            {"file": str(item[0]), "line": item[1], "href": item[2], "expected": item[3]}
            for item in all_broken_int
        ]
    }
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
