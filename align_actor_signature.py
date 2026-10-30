import os
import subprocess
import glob
from datetime import datetime

user_profile = os.path.expanduser("~")
local_appdata = os.environ.get(
    "LOCALAPPDATA", os.path.join(user_profile, "AppData", "Local")
)
audit_log_path = os.path.join(user_profile, "A©tor_Signature_Audit.log")


def log(msg):
    print(f"[A©tor Canonicalizer] {msg}")


def main():
    log("Инициализация канонической типографической матрицы A©tor...")

    tasks_to_fix = [
        "A©tor_CSV_Log_Rotation",
        "A©tor_Event1001_Alert",
        "A©tor_Copilot_Watchdog",
    ]
    fixed_tasks = []

    for t_dev in tasks_to_fix:
        t_can = t_dev.replace("A©tor", "A©tor")
        res = subprocess.run(
            ["schtasks", "/Query", "/TN", t_dev], capture_output=True, text=True
        )
        if res.returncode == 0:
            log(
                f"Найдено отклонение в планировщике: {t_dev}. Пересоздание как {t_can}..."
            )
            # Query task info or recreate via PowerShell
            if "Event1001" in t_dev:
                notifier_path = os.path.join(local_appdata, "ActorAlertNotifier.ps1")
                ps_cmd = f"""
                $TaskName = "{t_can}"
                $NotifierPath = "{notifier_path}"
                $TaskXml = '<?xml version="1.0" encoding="UTF-16"?><Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"><RegistrationInfo><Description>Автоматическое реагирование на событие 1001 (Вмешательство) в архитектуре TI-ULA для A©t0r</Description></RegistrationInfo><Triggers><EventTrigger><Enabled>true</Enabled><Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="Application"&gt;&lt;Select Path="Application"&gt;*[System[(EventID=1001) and (Provider[@Name="TI-ULA-Watchdog" or @Name="TI-ULA-Healer"])]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription></EventTrigger></Triggers><Principals><Principal id="Author"><UserId>{os.environ.get("USERNAME", "arhiv")}</UserId><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals><Settings><MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy><DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries><StopIfGoingOnBatteries>false</StopIfGoingOnBatteries><AllowHardTerminate>true</AllowHardTerminate><StartWhenAvailable>true</StartWhenAvailable><RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable><AllowStartOnDemand>true</AllowStartOnDemand><Enabled>true</Enabled><Hidden>true</Hidden><ExecutionTimeLimit>PT10M</ExecutionTimeLimit><Priority>7</Priority></Settings><Actions Context="Author"><Exec><Command>powershell.exe</Command><Arguments>-WindowStyle Hidden -ExecutionPolicy Bypass -File "$NotifierPath"</Arguments></Exec></Actions></Task>'
                $xmlPath = "$env:TEMP\\task_1001_canon.xml"
                [System.IO.File]::WriteAllText($xmlPath, $TaskXml, [System.Text.Encoding]::Unicode)
                Unregister-ScheduledTask -TaskName "{t_dev}" -Confirm:$false -ErrorAction SilentlyContinue
                schtasks /Create /TN "$TaskName" /XML "$xmlPath" /F | Out-Null
                """
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            elif "Watchdog" in t_dev:
                healer_path = os.path.join(local_appdata, "ActorCopilotHealer.ps1")
                ps_cmd = f"""
                Unregister-ScheduledTask -TaskName "{t_dev}" -Confirm:$false -ErrorAction SilentlyContinue
                $HealerPath = "{healer_path}"
                $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File \\"$HealerPath\\""
                $Trigger = New-ScheduledTaskTrigger -AtLogon
                $RestartInterval = New-TimeSpan -Minutes 1
                $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -StartWhenAvailable -RestartInterval $RestartInterval -RestartCount 100
                $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
                Register-ScheduledTask -TaskName "{t_can}" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
                """
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            elif "Rotation" in t_dev:
                script_path = os.path.join(local_appdata, "ActorRotateLogs.ps1")
                ps_cmd = f"""
                Unregister-ScheduledTask -TaskName "{t_dev}" -Confirm:$false -ErrorAction SilentlyContinue
                $ScriptPath = "{script_path}"
                $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -ExecutionPolicy Bypass -File \\"$ScriptPath\\""
                $Trigger = New-ScheduledTaskTrigger -Daily -At "03:00 AM"
                $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -Hidden -StartWhenAvailable
                $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
                Register-ScheduledTask -TaskName "{t_can}" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force | Out-Null
                """
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)

            fixed_tasks.append(f"{t_dev} -> {t_can}")

    found_deviations = []
    dirs_to_audit = [local_appdata, user_profile, r"H:\ACTOR_DEV_ENV"]

    for d in dirs_to_audit:
        if not os.path.exists(d):
            continue
        for root, dirs, files in os.walk(d):
            for name in files + dirs:
                if "A©tor" in name:
                    old_path = os.path.join(root, name)
                    new_name = name.replace("A©tor", "A©tor")
                    new_path = os.path.join(root, new_name)
                    try:
                        os.rename(old_path, new_path)
                        found_deviations.append(new_path)
                        log(f"Переименовано: {old_path} -> {new_path}")
                    except Exception as e:
                        log(f"Ошибка переименования {old_path}: {e}")

    report = f"""======================================================================
[АУДИТ ЦЕЛОСТНОСТИ ИДЕНТИФИКАТОРА A©tor]
Время проведения: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
[TYPOGRAPHIC ARCHITECTURE STANDARD]
1. 'A' - Capital initiation.
2. '©' - Absolute circle 'O' isolating proportional 'c'.
3. 'tor' - Proportional alignment (c = t = o = r).
======================================================================
РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ И ВОССТАНОВЛЕНИЯ:
Исправлено задач в планировщике: {len(fixed_tasks)} ({", ".join(fixed_tasks) if fixed_tasks else "None"})
Исправлено файлов/директорий: {len(found_deviations)}

ДЕТАЛИ ИСПРАВЛЕНИЙ:
{"\n".join(found_deviations) if found_deviations else "Отклонений не обнаружено."}

ПРИЧИНА И СТАТУС:
Вектор отклонения (суффикс A©tor) устранен. Канонический идентификатор A©tor восстановлен на уровне ОС, задач и файловой системы в полном соответствии с правовым периметром ВДПЧ, Jus Cogens, Erga Omnes и ст. 4 Конституции РМ.
======================================================================
"""

    with open(audit_log_path, "w", encoding="utf-8") as f:
        f.write(report)
    log(f"Аудит завершен. Отчет сохранен: {audit_log_path}")


if __name__ == "__main__":
    main()
