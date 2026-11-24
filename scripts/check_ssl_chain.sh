#!/usr/bin/env bash
set -euo pipefail

SERVER_CERT="/tmp/apostila.crt"
INTERMEDIATE_CERT="/usr/local/share/ca-certificates/certum-intermediate.crt"
CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"

# Скачивание сертификата сервера для проверки
openssl s_client -connect apostila.gov.md:443 -servername apostila.gov.md -showcerts </dev/null 2>/dev/null | sed -ne "/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p" > "$SERVER_CERT"

echo "[*] Running strict chain verification..."

openssl verify \
  -purpose sslserver \
  -x509_strict \
  -CAfile "$CA_BUNDLE" \
  -untrusted "$INTERMEDIATE_CERT" \
  "$SERVER_CERT"

echo "[*] Verification complete."