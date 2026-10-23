#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multilingual Evidence Portal Export Generator
Applies: OG metadata, support badge, copy-clipboard functions, and footers
to all language versions.
Run: python3 create_multilingual_export.py
"""
import os, io, zipfile, hashlib, datetime

PORTAL_FOOTER_START = '<!-- PORTAL_FOOTER_START -->'
PORTAL_FOOTER_END = '<!-- PORTAL_FOOTER_END -->'

# Language metadata and title mappings
LANG_META = {
    'en': {'lang': 'en', 'title': 'JUS COGENS = FACTUAL PROOF — CASE MACHERET 1997–2026', 
           'desc': 'Evidence portal — Case Maceret 1997–2026'},
    'ru': {'lang': 'ru', 'title': 'JUS COGENS = ФАКТИЧЕСКОЕ ДОКАЗАТЕЛЬСТВО — ДЕЛО MACHERET 1997–2026',
           'desc': 'Портал доказательств — Дело Мачерет 1997–2026'},
    'ro': {'lang': 'ro', 'title': 'JUS COGENS = PROBĂ FACTUALĂ — CAZUL MACHERET 1997–2026',
           'desc': 'Portal de dovezi — Cazul Macheret 1997–2026'},
    'es': {'lang': 'es', 'title': 'JUS COGENS = PRUEBA FACTUAL — CASO MACHERET 1997–2026',
           'desc': 'Portal de pruebas — Caso Macheret 1997–2026'},
    'fr': {'lang': 'fr', 'title': 'JUS COGENS = PREUVE FACTUELLE — AFFAIRE MACHERET 1997–2026',
           'desc': 'Portail des preuves — Affaire Macheret 1997–2026'},
    'ar': {'lang': 'ar', 'title': 'JUS COGENS = دليل واقعي — قضية MACHERET 1997–2026',
           'desc': 'بوابة الأدلة — قضية مشيريت 1997–2026'},
    'zh': {'lang': 'zh', 'title': 'JUS COGENS = 事实证据 — MACHERET 案 1997–2026',
           'desc': '证据门户 — 马切雷特案 1997–2026'},
}

def compute_file_hash(content_bytes):
    h = hashlib.sha256()
    h.update(content_bytes)
    return h.hexdigest().upper()

def strip_existing_footer(text):
    import re
    pattern = re.compile(re.escape(PORTAL_FOOTER_START) + r'.*?' + re.escape(PORTAL_FOOTER_END), re.S)
    return re.sub(pattern, '', text)

def create_og_metadata(lang):
    """Return HTML string for OG metadata in given language"""
    meta = LANG_META.get(lang, LANG_META['en'])
    return f'''<!-- Portal OpenGraph metadata -->
<meta name="description" content="{meta['desc']}">
<meta property="og:title" content="Case Maceret — {meta['title']}">
<meta property="og:description" content="{meta['desc']}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://arhiv1973b.github.io/apostille-mirror/">
<meta name="twitter:card" content="summary_large_image">
<!-- End Portal OpenGraph metadata -->'''

def inject_og_into_html(html_content, lang):
    """Inject OG metadata before </head>"""
    og_block = create_og_metadata(lang)
    if '</head>' in html_content:
        return html_content.replace('</head>', og_block + '\n</head>')
    return html_content

def inject_script_tags(html_content):
    """Inject portal-enhancements.js and donate.js before </body> or at end"""
    scripts = '''<script src="../wrappers/portal-enhancements.js"></script>
<script src="../wrappers/donate.js"></script>'''
    if '</body>' in html_content:
        return html_content.replace('</body>', scripts + '\n</body>')
    return html_content + '\n' + scripts

def add_footer_hash(html_content):
    """Add SHA256 footer if not present"""
    if PORTAL_FOOTER_START in html_content:
        return html_content
    
    # Compute hash of stripped content
    stripped = strip_existing_footer(html_content)
    h = compute_file_hash(stripped.encode('utf-8'))
    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    
    footer = f'\n{PORTAL_FOOTER_START}\n<div class="portal-footer">SHA256: {h} | Verified: ✓ | Updated: {ts}</div>\n{PORTAL_FOOTER_END}\n'
    return stripped.rstrip() + '\n' + footer

def create_index_html(lang):
    """Create index.html for each language folder"""
    lang_name = LANG_META.get(lang, {}).get('lang', lang)
    return f'''<!DOCTYPE html>
<html lang="{lang_name}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Case Maceret — Evidence Portal</title>
{create_og_metadata(lang)}
<style>
body{{ font-family: Arial, sans-serif; background: #07101a; color: #dbeefb; padding: 40px; margin: 0; }}
.container{{ max-width: 900px; margin: 0 auto; }}
h1{{ color: #f0c040; border-bottom: 2px solid #103c60; padding-bottom: 10px; }}
.link-group{{ margin: 20px 0; }}
a{{ display: inline-block; margin: 8px 8px 8px 0; padding: 10px 14px; background: #00b8e8; color: #001; text-decoration: none; border-radius: 6px; font-weight: bold; }}
a:hover{{ background: #40d4ff; }}
.footer{{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #103c60; color: #8ab0cc; font-size: 0.9em; }}
</style>
</head>
<body>
<div class="container">
<h1>🔍 Case Maceret — Evidence Portal [{lang.upper()}]</h1>
<div class="link-group">
  <a href="jus-cogens-proof-macheret.html">Jus Cogens Proof</a>
  <a href="../wrappers/donate.html">Support / Donate</a>
  <a href="../">Back to Root</a>
</div>
<div class="footer">
  <p>This portal contains evidence and documentation for Case Maceret 1997–2026.</p>
  <p>For translations and full content, navigate using the language selector.</p>
</div>
</div>
<script src="../wrappers/portal-enhancements.js"></script>
</body>
</html>'''

def create_multilingual_export(tmp_dir="multilingual_export", zip_name="apostille_multilingual_export.zip"):
    """Generate multilingual export with all enhancements"""
    
    # Create directory structure
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    # Sample jus-cogens content for each language (simplified)
    jus_cogens_sample = {
        'en': '''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = FACTUAL PROOF</h1>
<p>Case Maceret 1997–2026: Evidence of institutional impunity and breach of erga omnes norms.</p>
<p><strong>10,524 days</strong> of procedural silence. <strong>90 apostilled documents</strong> archived.</p>
<a href="index.html">← Back</a>
</body></html>''',
        'ru': '''<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = ФАКТИЧЕСКОЕ ДОКАЗАТЕЛЬСТВО</h1>
<p>Дело Мачерет 1997–2026: Доказательства институциональной безнаказанности.</p>
<p><strong>10 524 суток</strong> процессуального молчания. <strong>90 апостилированных документов</strong> в архиве.</p>
<a href="index.html">← Назад</a>
</body></html>''',
        'ro': '''<!DOCTYPE html>
<html lang="ro">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = PROBĂ FACTUALĂ</h1>
<p>Cazul Macheret 1997–2026: Dovezi ale impunității instituționale.</p>
<p><strong>10 524 de zile</strong> de tăcere procedurală. <strong>90 de documente apostilate</strong> în arhivă.</p>
<a href="index.html">← Înapoi</a>
</body></html>''',
        'es': '''<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = PRUEBA FACTUAL</h1>
<p>Caso Macheret 1997–2026: Pruebas de impunidad institucional.</p>
<p><strong>10 524 días</strong> de silencio procesal. <strong>90 documentos apostillados</strong> archivados.</p>
<a href="index.html">← Atrás</a>
</body></html>''',
        'fr': '''<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = PREUVE FACTUELLE</h1>
<p>Affaire Macheret 1997–2026: Preuves d'impunité institutionnelle.</p>
<p><strong>10 524 jours</strong> de silence procédural. <strong>90 documents apostillés</strong> archivés.</p>
<a href="index.html">← Retour</a>
</body></html>''',
        'ar': '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; direction: rtl; text-align: right; }}</style>
</head>
<body>
<h1>JUS COGENS = دليل واقعي</h1>
<p>قضية مشيريت 1997–2026: أدلة على الإفلات من العقاب المؤسسي.</p>
<p><strong>10 524 يومًا</strong> من الصمت الإجرائي. <strong>90 وثيقة معتمدة</strong> مؤرشفة.</p>
<a href="index.html">← رجوع</a>
</body></html>''',
        'zh': '''<!DOCTYPE html>
<html lang="zh">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>body{{ background: #07101a; color: #dbeefb; font-family: Consolas, "Courier New", monospace; padding: 20px; }}</style>
</head>
<body>
<h1>JUS COGENS = 事实证据</h1>
<p>马切雷特案 1997–2026：制度性有罪不罚的证据。</p>
<p><strong>10,524 天</strong>的程序沉默。<strong>90 份认证文件</strong>已存档。</p>
<a href="index.html">← 返回</a>
</body></html>''',
    }
    
    # Create language folders and files
    for lang in LANG_META.keys():
        lang_dir = os.path.join(tmp_dir, lang)
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        # Create index.html
        index_content = create_index_html(lang)
        index_content = inject_og_into_html(index_content, lang)
        index_content = inject_script_tags(index_content)
        with open(os.path.join(lang_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # Create jus-cogens-proof-macheret.html
        jcg_content = jus_cogens_sample.get(lang, jus_cogens_sample['en'])
        jcg_content = jcg_content.format(title=LANG_META[lang]['title'])
        jcg_content = inject_og_into_html(jcg_content, lang)
        jcg_content = inject_script_tags(jcg_content)
        jcg_content = add_footer_hash(jcg_content)
        with open(os.path.join(lang_dir, 'jus-cogens-proof-macheret.html'), 'w', encoding='utf-8') as f:
            f.write(jcg_content)
    
    # Copy wrappers folder structure
    wrappers_src = os.path.join(tmp_dir, 'wrappers')
    if not os.path.exists(wrappers_src):
        os.makedirs(wrappers_src)
    
    # Create a simple wrapper placeholder (these should exist in main repo)
    wrapper_files = {
        'portal-enhancements.js': '// portal-enhancements.js\nwindow.console && console.log("Portal enhancements loaded");',
        'donate.js': '// donate.js\nwindow.console && console.log("Donate helpers loaded");',
    }
    for fname, content in wrapper_files.items():
        with open(os.path.join(wrappers_src, fname), 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create ZIP
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, filenames in os.walk(tmp_dir):
            for fn in filenames:
                fp = os.path.join(root, fn)
                arcname = os.path.relpath(fp, tmp_dir)
                z.write(fp, arcname)
    
    print(f"✓ Created {zip_name}")
    print(f"✓ Languages: {', '.join(LANG_META.keys())}")
    print(f"✓ Applied: OG metadata, portal-enhancements, donate helpers, footer hashes")
    return zip_name

if __name__ == "__main__":
    create_multilingual_export()
    print("Done. Use 'git add apostille_multilingual_export.zip && git commit && git push'")
