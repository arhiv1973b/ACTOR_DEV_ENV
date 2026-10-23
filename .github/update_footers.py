#!/usr/bin/env python3
import hashlib, os, re, datetime, sys, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(ROOT, '..'))
FOOTER_START = '<!-- PORTAL_FOOTER_START -->'
FOOTER_END = '<!-- PORTAL_FOOTER_END -->'

def compute_hash(content_bytes):
    h = hashlib.sha256()
    h.update(content_bytes)
    return h.hexdigest().upper()

def strip_existing_footer(text):
    pattern = re.compile(re.escape(FOOTER_START) + r'.*?' + re.escape(FOOTER_END), re.S)
    return re.sub(pattern, '', text)

changed = []
for dirpath, dirs, files in os.walk(REPO_ROOT):
    # skip .git
    if '.git' in dirpath.split(os.sep):
        continue
    for f in files:
        if f.lower().endswith('.html'):
            path = os.path.join(dirpath, f)
            with open(path, 'rb') as fh:
                raw = fh.read()
            try:
                text = raw.decode('utf-8')
            except:
                try:
                    text = raw.decode('cp1251')
                except:
                    text = raw.decode('utf-8', errors='ignore')
            stripped = strip_existing_footer(text)
            # compute hash of stripped content (utf-8)
            h = compute_hash(stripped.encode('utf-8'))
            ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
            footer = '\n' + FOOTER_START + '\n' + f'<div class="portal-footer">SHA256: {h} | Verified: ✓ | Updated: {ts}</div>' + '\n' + FOOTER_END + '\n'
            new_text = stripped.rstrip() + '\n' + footer
            if new_text != text:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(new_text)
                changed.append(os.path.relpath(path, REPO_ROOT))

if changed:
    print('Updated footers on:', changed)
    # commit changes
    try:
        subprocess.check_call(['git', 'config', 'user.name', 'auto-footer-bot'])
        subprocess.check_call(['git', 'config', 'user.email', 'auto-footer-bot@example.com'])
        subprocess.check_call(['git', 'add'] + changed)
        subprocess.check_call(['git', 'commit', '-m', f'Auto-update portal footers ({len(changed)} files)'])
        subprocess.check_call(['git', 'push', 'origin', 'HEAD'])
    except subprocess.CalledProcessError as e:
        print('Git commit/push failed:', e)
        sys.exit(2)
else:
    print('No footer changes required.')
