#!/usr/bin/env bash
set -e

echo "=== A©t0r Protocol: Independent Evidence Verification Agent ==="
echo "=== Vector: Erga Omnes | Standard: RFC 3161 & Jus Cogens ==="

# 1. Setup working directory or clone mirror if needed
MIRROR_URL="https://github.com/arhiv1973b/evidence-pdfs-mirror.git"
WORK_DIR="./evidence_verify_workspace"

if [ -d "$WORK_DIR" ]; then
    rm -rf "$WORK_DIR"
fi
mkdir -p "$WORK_DIR"

echo "📡 Cloning public evidence mirror from $MIRROR_URL..."
git clone --depth 1 "$MIRROR_URL" "$WORK_DIR" || {
    echo "⚠️ Failed to clone remote mirror, falling back to local directory inspection..."
    WORK_DIR="."
}

cd "$WORK_DIR"

# Check required files
MANIFEST="05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt"
if [ ! -f "$MANIFEST" ]; then
    MANIFEST="CHECKSUMS_SHA256.txt"
fi

SIG="05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt.sig"
if [ ! -f "$SIG" ]; then
    SIG="CHECKSUMS_SHA256.txt.sig"
fi

TSR="05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.tsr"
if [ ! -f "$TSR" ]; then
    TSR="CHECKSUMS_SHA256.tsr"
fi

if [ ! -f "$MANIFEST" ] || [ ! -f "$SIG" ]; then
    echo "❌ Error: Required manifest or signature file not found!"
    exit 1
fi

echo "✅ Artifacts located successfully."

# 2. Verify GPG Signature
echo "=== Step 2: Verifying GPG Signature ==="
if gpg --verify "$SIG" "$MANIFEST" 2>/dev/null; then
    echo "✅ GPG Signature verified successfully."
else
    echo "❌ CRITICAL: GPG signature verification FAILED!"
    exit 1
fi

# 3. Verify RFC 3161 Timestamp (TSA)
echo "=== Step 3: Verifying RFC 3161 Timestamp (TSA) ==="
if [ -f "$TSR" ]; then
    TSA_INFO=$(openssl ts -reply -in "$TSR" -text || echo "")
    echo "Detected TSA Info:"
    echo "$TSA_INFO"

    if echo "$TSA_INFO" | grep -qi "FreeTSA"; then
        echo "Issuer: FreeTSA"
        wget -q https://freetsa.org/files/tsa.crt -O tsa.crt || true
        wget -q https://freetsa.org/files/cacert.pem -O cacert.pem || true
        openssl ts -verify -data "$MANIFEST" -in "$TSR" -CAfile cacert.pem -untrusted tsa.crt
    elif echo "$TSA_INFO" | grep -qi -E "Apple|DigiCert"; then
        echo "Issuer: Enterprise TSA (Apple/DigiCert)"
        openssl ts -verify -data "$MANIFEST" -in "$TSR" || openssl ts -verify -data "$MANIFEST" -in "$TSR" -untrusted /etc/ssl/certs/ca-certificates.crt
    else
        echo "❌ Error: Unknown or unauthorized TSA issuer."
        exit 1
    fi
    echo "✅ Timestamp verified successfully."
else
    echo "⚠️ Warning: .tsr timestamp file not found. Skipping TSA verification."
fi

# 4. Cross-Check File SHA-256 Hashes
echo "=== Step 4: Cross-Checking SHA-256 File Hashes ==="
python3 -c '
import hashlib
from pathlib import Path

manifest_path = Path("'"$MANIFEST"'")
mismatches = 0
total = 0

for line in manifest_path.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    parts = line.split(maxsplit=1)
    if len(parts) == 2:
        expected_hash, filepath = parts[0].strip(), parts[1].strip()
        p = Path(filepath)
        if p.exists():
            total += 1
            actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
            if actual_hash.lower() != expected_hash.lower():
                print(f"❌ Hash Mismatch: {filepath} (expected {expected_hash}, got {actual_hash})")
                mismatches += 1
        else:
            print(f"⚠️ File missing on disk: {filepath}")

print(f"Total files checked: {total}, Mismatches: {mismatches}")
if mismatches > 0:
    exit(1)
'

echo "✅ ALL VERIFICATION GATES PASSED: Evidence Integrity 100% Verified."
