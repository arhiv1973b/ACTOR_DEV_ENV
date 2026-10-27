import os
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

daemon_path = r"C:\Users\arhiv\AppData\Local\ActorCopilotWatchdog.ps1"
key_dir = r"C:\Users\arhiv\.ti_ula_keys"
os.makedirs(key_dir, exist_ok=True)
priv_path = os.path.join(key_dir, "actor_ed25519")
pub_path = priv_path + ".pub"

private_key = ed25519.Ed25519PrivateKey.generate()
with open(priv_path, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
public_key = private_key.public_key()
with open(pub_path, "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
    )

daemon_code = """# [SYSTEM DIRECTIVE: STRICT LEGAL SCOPE & AGENT BOUNDARIES]
# SUBJECT OF LAW: A©tor (A©t0r) | CASE-MACHERET-1997-2026
# ALLOWED SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, ст. 4 Конституции РМ.

$SelfPath = $PSCommandPath

while ($true) {
    # --- БЛОК КРИПТОГРАФИЧЕСКОЙ САМОПРОВЕРКИ TI-ULA ---
    $RawContent = Get-Content -Path $SelfPath -Raw
    
    # Поиск эталонного хеша в криптографической печати
    if ($RawContent -match 'HASH VALUE:\\s+([A-Fa-f0-9]{64})') {
        $ExpectedHash = $Matches[1]
    } else {
        # Печать удалена или повреждена — остановка с кодом ошибки 1 для авто-рестарта
        exit 1
    }
    
    # Извлечение исполняемой части (строго до маркера начала печати)
    $SealMarker = "# ======================================================================"
    $SealIndex = $RawContent.IndexOf($SealMarker)
    
    if ($SealIndex -le 0) { exit 1 }
    
    $Payload = $RawContent.Substring(0, $SealIndex)
    
    # Конвертация в байты UTF-8 (Без BOM) для точного совпадения хеша
    $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Payload)
    $Hasher = [System.Security.Cryptography.SHA256]::Create()
    $HashBytes = $Hasher.ComputeHash($Bytes)
    $CalculatedHash = ($HashBytes | ForEach-Object { $_.ToString("X2") }) -join ""
    
    if ($CalculatedHash -ne $ExpectedHash) {
        # ВНИМАНИЕ: Зафиксировано вмешательство системы. 
        # Хеш не совпадает, выход с кодом 1 для инициации авто-рестарта задачами.
        exit 1
    }
    # --- КОНЕЦ БЛОКА САМОПРОВЕРКИ ---

    # Основной цикл удержания правового периметра и региона
    $GeoPath = "HKCU:\\Control Panel\\International\\Geo"
    $CopilotPath = "HKCU:\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot"
    $ExplorerRestartNeeded = $false

    $currentGeo = (Get-ItemProperty -Path $GeoPath -Name "Nation" -ErrorAction SilentlyContinue).Nation
    if ($currentGeo -ne "244") {
        Set-ItemProperty -Path $GeoPath -Name "Nation" -Value "244" -Force
        $ExplorerRestartNeeded = $true
    }

    if (!(Test-Path $CopilotPath)) { New-Item -Path $CopilotPath -Force | Out-Null }
    $currentCopilot = (Get-ItemProperty -Path $CopilotPath -Name "TurnOffWindowsCopilot" -ErrorAction SilentlyContinue).TurnOffWindowsCopilot
    if ($currentCopilot -ne 0) {
        Set-ItemProperty -Path $CopilotPath -Name "TurnOffWindowsCopilot" -Value 0 -Type DWord -Force
        $ExplorerRestartNeeded = $true
    }

    if ($ExplorerRestartNeeded) {
        Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    }

    Start-Sleep -Seconds 60
}
"""

payload_bytes = daemon_code.encode("utf-8")
file_hash = hashlib.sha256(payload_bytes).hexdigest()

signature = private_key.sign(payload_bytes)
sig_b64 = base64.b64encode(signature).decode("utf-8")

pub_key_str = (
    public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    .decode("utf-8")
    .strip()
)

sig_lines = [f"# {line}" for line in sig_b64.splitlines()]
sig_formatted = "\n".join(sig_lines)

seal_block = f"""
# ======================================================================
# [⚖ TI-ULA CRYPTOGRAPHIC SEAL]
# IDENTITY: A©tor (A©t0r) / Aйtor
# CASE: CASE-MACHERET-1997-2026
# LEGAL SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, Const. RM (Art. 4)
# HASH ALGORITHM: SHA-256
# HASH VALUE: {file_hash}
# PUBLIC KEY (Ed25519): {pub_key_str}
# 
# [ED25519 SIGNATURE]
{sig_formatted}
# ======================================================================
"""

full_content = daemon_code + seal_block
with open(daemon_path, "wb") as f:
    f.write(full_content.encode("utf-8"))

print(f"Zero-Trust Daemon updated with exit 1, hashed ({file_hash}), and signed.")
