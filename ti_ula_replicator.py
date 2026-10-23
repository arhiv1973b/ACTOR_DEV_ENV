import os
import subprocess
import json

# TI-ULA REPLICATION & DISASTER RECOVERY CONTOUR (RCLONE / MIRROR)
# Case: CASE-MACHERET-1997-2026 | Protocol: Erga Omnes Anti-Seizure Protection

TARGET_VAULTS = [
    "CADASTRAL_RECORDS",
    "MUNICIPAL_ARCHIVE_DUPLICATES",
    "PROPERTY_ALLOCATIONS",
]
REMOTE_TARGET = "ti-ula-encrypted-remote:case-macheret-vault"


def sync_to_decentralized_cloud():
    print("=== TI-ULA REPLICATOR: INITIATING DECENTRALIZED CLOUD SYNC ===")

    # Check if rclone is available
    rclone_check = subprocess.run(["rclone", "version"], capture_output=True, text=True)
    if rclone_check.returncode != 0:
        print(
            "[!] rclone not configured in path. Generating rclone configuration template..."
        )
        config_template = """
[ti-ula-encrypted-remote]
type = crypt
remote = remote:ti-ula-vault-encrypted
password = derived-from-case-macheret-1997-2026-salt
"""
        with open("rclone_template.conf", "w", encoding="utf-8") as f:
            f.write(config_template.strip())
        print("[✓] Generated rclone_template.conf. Configure remote when operational.")
        return False

    success = True
    for vault in TARGET_VAULTS:
        if os.path.exists(vault) and os.listdir(vault):
            cmd = ["rclone", "sync", vault, f"{REMOTE_TARGET}/{vault}", "--fast-list"]
            print(f"[>] Syncing vault {vault} to decentralized remote...")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[✓] Successfully mirrored {vault} to decentralized cloud.")
            else:
                print(f"[!] Replication warning for {vault}: {res.stderr.strip()}")
                success = False
        else:
            print(f"[-] Vault {vault} is empty or missing. Skipping sync.")

    return success


if __name__ == "__main__":
    sync_to_decentralized_cloud()
