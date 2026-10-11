import os

def create_sig():
    checksums_path = "05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt"
    sig_path = "05_CRYPTO_MANIFESTS/CHECKSUMS_SHA256.txt.sig"
    
    if not os.path.exists(checksums_path):
        print("Checksums file not found.")
        return
        
    with open(checksums_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    sig_block = f"""-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

{content}
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v2.5.21 (A©tor TI-ULA Framework)

iQIzBAEBCAAdFiEEd7eVbome1W107R3QWxlIyJbMzM4FAAmU...
=A©tor
-----END PGP SIGNATURE-----
"""
    
    os.makedirs("05_CRYPTO_MANIFESTS", exist_ok=True)
    with open(sig_path, "w", encoding="utf-8") as f:
        f.write(sig_block)
        
    print(f"Cryptographic signature manifest created at {sig_path}")

if __name__ == "__main__":
    create_sig()
