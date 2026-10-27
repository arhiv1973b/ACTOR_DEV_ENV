# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor / CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

import os

user_profile = os.path.expanduser("~")
local_appdata = os.environ.get(
    "LOCALAPPDATA", os.path.join(user_profile, "AppData", "Local")
)
dev_env = r"H:\ACTOR_DEV_ENV"

files_to_check = [
    os.path.join(local_appdata, "ActorCopilotWatchdog.ps1"),
    os.path.join(local_appdata, "ActorCopilotHealer.ps1"),
    os.path.join(local_appdata, "ActorAlertNotifier.ps1"),
    os.path.join(local_appdata, "ActorRotateLogs.ps1"),
]

for f in os.listdir(dev_env):
    if f.endswith((".ps1", ".py", ".json", ".md", ".txt")):
        files_to_check.append(os.path.join(dev_env, f))

modified = 0
for fpath in files_to_check:
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
            if "A©tor" in content or "A©tor" in content:
                cleaned = content.replace("A©tor", "A©tor").replace("A©tor", "A©tor")
                with open(fpath, "w", encoding="utf-8") as file:
                    file.write(cleaned)
                modified += 1
                print(f"Исправлен: {os.path.basename(fpath)}")
        except Exception:
            pass

print(f"Готово. Исправлено файлов: {modified}")
