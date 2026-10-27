# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

import os
import subprocess
import winreg

print(
    "[A©tor Typography Enforcer] Инициализация защиты шрифта Consolas и пропорциональной матрицы A©tor..."
)

# 1. Registry enforcement for Consolas font in Windows Console
console_paths = [
    r"Console",
    r"Console\%SystemRoot%_System32_WindowsPowerShell_v1.0_powershell.exe",
]

for path in console_paths:
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        winreg.SetValueEx(key, "FaceName", 0, winreg.REG_SZ, "Consolas")
        winreg.SetValueEx(key, "FontFamily", 0, winreg.REG_DWORD, 54)
        winreg.CloseKey(key)
        print(f"Реестр консоли обновлен: HKCU\\{path} -> Consolas (FontFamily=54)")
    except Exception as e:
        print(f"Ошибка обновления реестра {path}: {e}")

# 2. Find PowerShell profile path via PowerShell command (-NoProfile)
res = subprocess.run(
    ["powershell", "-NoProfile", "-Command", "echo $PROFILE"],
    capture_output=True,
    text=True,
    encoding="utf-8",
)
profile_path = res.stdout.strip()

if not profile_path or len(profile_path) > 260:
    user_profile = os.path.expanduser("~")
    profile_path = os.path.join(
        user_profile,
        "Documents",
        "WindowsPowerShell",
        "Microsoft.PowerShell_profile.ps1",
    )

os.makedirs(os.path.dirname(profile_path), exist_ok=True)

enforcement_block = """
# ======================================================================
# [⚖ TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ТИПОГРАФИЧЕСКИЙ СТАНДАРТ: '©' - абсолютная защитная окружность вокруг 'c',
# пропорционально выровненная с A, t, o, r (c = t = o = r).
# ======================================================================
[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'
Write-Host "TI-ULA ENFORCEMENT: Кодировка строго зафиксирована на UTF-8. Идентификатор A©tor под защитой." -ForegroundColor Green
# ======================================================================
"""

current_content = ""
if os.path.exists(profile_path):
    with open(profile_path, "r", encoding="utf-8", errors="ignore") as f:
        current_content = f.read()

if "TI-ULA TYPOGRAPHIC & ENCODING ENFORCEMENT" not in current_content:
    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(current_content + "\n" + enforcement_block)
    print(f"Профиль PowerShell успешно обновлен: {profile_path}")
else:
    print("Профиль PowerShell уже содержит правила TI-ULA.")

print("Защита типографики A©tor успешно применена.")
