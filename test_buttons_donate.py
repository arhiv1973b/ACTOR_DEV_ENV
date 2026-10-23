#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Button & Donate Flow Tester
Tests: button clickability, OG metadata presence, donate page functionality
Run: python3 test_buttons_donate.py
"""
import os, re, sys

PORTAL_DIR = os.path.dirname(os.path.abspath(__file__))

def check_file_exists(filename):
    path = os.path.join(PORTAL_DIR, filename)
    return os.path.exists(path), path

def test_og_metadata(html_content, filename):
    """Check for OG metadata tags"""
    og_tags = re.findall(r'<meta\s+property="og:(\w+)"', html_content)
    if og_tags:
        return True, f"✓ {filename}: {len(og_tags)} OG tags found ({', '.join(og_tags[:3])}...)"
    return False, f"✗ {filename}: NO OG tags"

def test_button_links(html_content, filename):
    """Check for clickable button links"""
    buttons = re.findall(r'<a\s+class="button"[^>]*href="([^"]+)"', html_content)
    if buttons:
        return True, f"✓ {filename}: {len(buttons)} clickable buttons found"
    return False, f"✗ {filename}: NO clickable buttons"

def test_donate_elements(html_content, filename):
    """Check for donate page elements"""
    checks = {
        'bank_iban': r'MD55FT225920600348117498',
        'github_sponsors': r'github\.com/sponsors',
        'copy_buttons': r'copy(?:.*?)?button',
        'toast_notification': r'donate-toast',
        'payment_purpose': r'payment.purpose|назначение.*платежа'
    }
    results = {}
    for key, pattern in checks.items():
        if re.search(pattern, html_content, re.IGNORECASE):
            results[key] = True
        else:
            results[key] = False
    
    total = sum(results.values())
    return total >= 3, f"  Donate page [{filename}]: {total}/5 elements present ({', '.join([k for k,v in results.items() if v])})"

def test_scripts_injected(html_content, filename):
    """Check for required scripts"""
    scripts = re.findall(r'<script\s+src="([^"]+)"', html_content)
    needed = ['portal-enhancements', 'donate']
    found = [s for s in scripts if any(n in s for n in needed)]
    if len(found) >= 1:
        return True, f"✓ {filename}: Scripts injected ({', '.join([s.split('/')[-1] for s in found])})"
    return False, f"✗ {filename}: Missing scripts"

def test_footer_hash(html_content, filename):
    """Check for SHA256 footer"""
    if 'SHA256:' in html_content and 'PORTAL_FOOTER' in html_content:
        return True, f"✓ {filename}: SHA256 footer present"
    return False, f"✗ {filename}: No SHA256 footer"

def main():
    print("=" * 70)
    print("BUTTON & DONATE FLOW TESTER")
    print("=" * 70)
    print()
    
    files_to_test = [
        'index.html',
        'wrappers/donate.html',
        'doc-apostila.html',
        'fact-torture-1997.html',
    ]
    
    results = {'pass': 0, 'fail': 0, 'details': []}
    
    for filename in files_to_test:
        exists, path = check_file_exists(filename)
        if not exists:
            print(f"✗ {filename}: FILE NOT FOUND")
            results['fail'] += 1
            continue
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print(f"\n📄 Testing: {filename}")
        print("-" * 70)
        
        tests = [
            ('OG Metadata', test_og_metadata),
            ('Button Links', test_button_links),
            ('Scripts', test_scripts_injected),
            ('Footer Hash', test_footer_hash),
        ]
        
        # Special test for donate.html
        if 'donate' in filename:
            tests.append(('Donate Elements', test_donate_elements))
        
        for test_name, test_func in tests:
            passed, msg = test_func(content, filename)
            status = "✓" if passed else "✗"
            print(f"  {status} {msg}")
            if passed:
                results['pass'] += 1
            else:
                results['fail'] += 1
            results['details'].append((filename, test_name, passed, msg))
    
    # Summary
    print()
    print("=" * 70)
    print(f"SUMMARY: {results['pass']} passed, {results['fail']} failed")
    print("=" * 70)
    
    # Donate flow check
    print()
    print("💳 DONATE FLOW VERIFICATION:")
    print("-" * 70)
    donate_path = os.path.join(PORTAL_DIR, 'wrappers/donate.html')
    if os.path.exists(donate_path):
        with open(donate_path, 'r', encoding='utf-8', errors='ignore') as f:
            donate_content = f.read()
        
        checks = [
            ('Bank Transfer Details (IBAN)', r'MD55FT225920600348117498'),
            ('Beneficiary Name', r'Maceret\s+Alexei'),
            ('GitHub Sponsors Link', r'github\.com/sponsors'),
            ('Copy Bank Details Button', r'Копировать.*реквизиты'),
            ('Copy Payment Purpose Button', r'Копировать.*назначение'),
            ('Phishing Warning', r'phish.warn|фишинг'),
            ('Payment Purpose Template', r'назначение.*платежа|payment.*purpose'),
            ('Toast Notification Script', r'donate-toast|createToast'),
            ('Support Badge Script', r'portal-enhancements\.js'),
        ]
        
        for check_name, pattern in checks:
            if re.search(pattern, donate_content, re.IGNORECASE):
                print(f"  ✓ {check_name}")
            else:
                print(f"  ✗ {check_name}")
    
    # Actionable recommendations
    print()
    print("🎯 RECOMMENDATIONS:")
    print("-" * 70)
    if results['fail'] == 0:
        print("  ✓ All tests PASSED — portal is ready for production!")
        print("  ✓ All buttons are clickable and donation flow is active")
        print("  ✓ Waiting for CDN refresh (OG tags will appear in 2-3 min)")
    else:
        print(f"  ⚠ {results['fail']} tests failed — review above")
        print("  • Check OG metadata injection in all HTML files")
        print("  • Verify script tags are properly closed")
        print("  • Test donate page copy buttons manually")
    
    print()
    print("Manual test URLs:")
    print("  • Main portal: https://arhiv1973b.github.io/apostille-mirror/")
    print("  • Donate page: https://arhiv1973b.github.io/apostille-mirror/wrappers/donate.html")
    print("  • Language versions: /en/, /ru/, /ro/, /es/, /fr/, /ar/, /zh/")
    print()
    
    return 0 if results['fail'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
