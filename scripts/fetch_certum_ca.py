from __future__ import annotations
import hashlib
from pathlib import Path
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)

# Актуальный официальный URL цепочки Certum DV (Domain Validation) SHA2, содержащий Intermediate CA
CERTUM_CA_URL = "https://repository.certum.pl/bundles/DVSSLChain-SHA2.crt"

def fetch_and_save_ca(output_dir: str | Path = "certs") -> bool:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    cert_file = out_path / "certum-intermediate.crt"
    sha_file = out_path / "certum-intermediate.sha256"

    LOGGER.info(f"[*] Загрузка цепочки/сертификата Certum CA с URL: {CERTUM_CA_URL}")
    
    try:
        response = requests.get(CERTUM_CA_URL, timeout=30)
        response.raise_for_status()
        cert_data = response.content

        # Проверяем формат и приводим к PEM, если необходимо
        if b"-----BEGIN CERTIFICATE-----" not in cert_data:
            import base64
            encoded = base64.b64encode(cert_data).decode("ascii")
            lines = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
            pem_data = "-----BEGIN CERTIFICATE-----\n" + "\n".join(lines) + "\n-----END CERTIFICATE-----\n"
            cert_bytes = pem_data.encode("utf-8")
        else:
            cert_bytes = cert_data

        # Сохраняем промежуточный сертификат / бандл
        with open(cert_file, "wb") as f:
            f.write(cert_bytes)
        LOGGER.info(f"[+] Сертификат/бандл успешно сохранен в: {cert_file}")

        # Вычисляем SHA-256 хэш
        sha256_hash = hashlib.sha256(cert_bytes).hexdigest().upper()
        
        # Сохраняем хэш
        with open(sha_file, "w", encoding="utf-8") as f:
            f.write(sha256_hash)
        LOGGER.info(f"[+] SHA-256 хэш записан в {sha_file}: {sha256_hash}")

        return True

    except Exception as e:
        LOGGER.error(f"[X] Ошибка при загрузке Certum CA: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = fetch_and_save_ca()
    if not success:
        sys.exit(1)
    else:
        print("[OK] Корректный промежуточный сертификат Certum успешно загружен и обновлен.")
