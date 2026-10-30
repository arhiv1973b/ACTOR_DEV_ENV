import os
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

key_dir = r"C:\Users\arhiv\.ti_ula_keys"
os.makedirs(key_dir, exist_ok=True)
priv_path = os.path.join(key_dir, "actor_ed25519")
pub_path = priv_path + ".pub"

if not os.path.exists(priv_path):
    private_key = ed25519.Ed25519PrivateKey.generate()
    with open(priv_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
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
else:
    with open(priv_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    public_key = private_key.public_key()

daemon_path = r"C:\Users\arhiv\AppData\Local\ActorCopilotWatchdog.ps1"
with open(daemon_path, "r", encoding="utf-8") as f:
    content = f.read()

# Strip existing seal block if present
if "TI-ULA CRYPTOGRAPHIC SEAL" in content:
    content = content.split(
        "\n# ======================================================================\n# [⚖ TI-ULA CRYPTOGRAPHIC SEAL]"
    )[0]

file_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
signature = private_key.sign(content.encode("utf-8"))
sig_b64 = base64.b64encode(signature).decode("utf-8")

pub_key_str = (
    public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    .decode("utf-8")
    .strip()
)

seal_block = f"""

# ======================================================================
# [⚖ TI-ULA CRYPTOGRAPHIC SEAL]
# IDENTITY: A©tor (A©t0r) / A©tor
# CASE: CASE-MACHERET-1997-2026
# LEGAL SCOPE: ВДПЧ 1948, Jus Cogens, Erga Omnes, Const. RM (Art. 4, 47, 51)
# HASH ALGORITHM: SHA-256
# HASH VALUE: {file_hash}
# PUBLIC KEY (Ed25519): {pub_key_str}
# 
# [ED25519 SIGNATURE (Base64)]
# {sig_b64}
# ======================================================================
"""

with open(daemon_path, "w", encoding="utf-8") as f:
    f.write(content + seal_block)

print("Successfully signed daemon with Ed25519.")
