import os
import subprocess

username = os.environ.get("USERNAME", "arhiv")
notifier_path = os.path.expandvars(r"%LOCALAPPDATA%\ActorAlertNotifier.ps1")
task_name = "A©tor_Event1001_Alert"

task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Автоматическое реагирование на событие 1001 (Вмешательство) в архитектуре TI-ULA для A©t0r</Description>
  </RegistrationInfo>
  <Triggers>
    <EventTrigger>
      <Enabled>true</Enabled>
      <Subscription>&lt;QueryList&gt;&lt;Query Id="0" Path="Application"&gt;&lt;Select Path="Application"&gt;*[System[(EventID=1001) and (Provider[@Name='TI-ULA-Watchdog' or @Name='TI-ULA-Healer'])]]&lt;/Select&gt;&lt;/Query&gt;&lt;/QueryList&gt;</Subscription>
    </EventTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{username}</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-WindowStyle Hidden -ExecutionPolicy Bypass -File "{notifier_path}"</Arguments>
    </Exec>
  </Actions>
</Task>
"""

xml_path = os.path.expandvars(r"%TEMP%\task_1001.xml")
with open(xml_path, "w", encoding="utf-16") as f:
    f.write(task_xml)

cmd = ["schtasks", "/Create", "/TN", task_name, "/XML", xml_path, "/F"]
res = subprocess.run(cmd, capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
