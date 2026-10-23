import pathlib
from cryptography.hazmat.primitives import serialization

BASE_DIR = pathlib.Path(__file__).parent.resolve()
PRIV_KEY = BASE_DIR / "private_key.pem"
MANIFEST = BASE_DIR / "evidence_manifest.json"
SIG_FILE = BASE_DIR / "manifest.sig"

def sign():
    if not PRIV_KEY.exists():
        print(f"❌ Ключ не найден: {PRIV_KEY}")
        return
    
    with open(PRIV_KEY, "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    
    manifest_bytes = MANIFEST.read_bytes()
    # Ed25519 подписывает данные одной командой без доп. параметров
    signature = private_key.sign(manifest_bytes)
    SIG_FILE.write_bytes(signature)
    print("✅ Манифест успешно подписан (Ed25519).")

if __name__ == "__main__":
    sign()
