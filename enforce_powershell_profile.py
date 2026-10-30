# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

import os
from pathlib import Path

home = Path.home()
docs = home / "Documents"
docs.mkdir(parents=True, exist_ok=True)
pwsh_dir = docs / "WindowsPowerShell"
pwsh_dir.mkdir(parents=True, exist_ok=True)
profile = pwsh_dir / "Microsoft.PowerShell_profile.ps1"

block = """
# ======================================================================
# [⚖ TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ЦЕЛЬ: Блокировка деградации символа '©' и защита архитектуры
# ======================================================================

[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "TI-ULA ENFORCEMENT: Кодировка строго зафиксирована на UTF-8. Идентификатор A©tor под защитой." -ForegroundColor Green
# ======================================================================
"""

content = ""
if profile.exists():
    try:
        content = profile.read_text(encoding="utf-8", errors="ignore")
    except:
        pass

if "TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT" not in content:
    profile.write_text(content + "\n" + block, encoding="utf-8")

Path(home / "debug_ok.txt").write_text("OK", encoding="utf-8")
