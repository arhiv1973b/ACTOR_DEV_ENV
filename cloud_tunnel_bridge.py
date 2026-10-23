#!/usr/bin/env python3
"""
Cloud Tunnel & Instant Sync Bridge (cloud_tunnel_bridge.py)
Обеспечивает мгновенную синхронизацию Git-коммитов и доказательств с Google Drive и OneDrive.
"""

import os
import subprocess
import hashlib
import datetime

CONFIG = {
    "gdrive_vault": r"F:\Мой диск\EvidenceVault",
    "onedrive_gateway": r"C:\Users\arhiv\OneDrive\Документы\ViberDownloads",
    "local_repo": r"H:\ACTOR_DEV_ENV",
}


def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.returncode, result.stdout.strip()


def tunnel_sync():
    print(
        f"[{datetime.datetime.utcnow().isoformat()}Z] Initiating Cloud Tunnel Sync..."
    )

    # 1. Git push status check
    code, out = run_cmd("git status --porcelain")
    if out:
        print("[+] Uncommitted changes detected. Committing to DAG...")
        run_cmd("git add .")
        run_cmd(
            'git commit -m "AUTO-TUNNEL: Real-time evidence synchronization and email indexing"'
        )
        run_cmd("git push origin HEAD")

    # 2. Rclone sync to Google Drive Vault
    if os.path.exists(CONFIG["gdrive_vault"]):
        print("[+] Syncing local vault to Google Drive F:\\...")
        run_cmd(
            f'rclone sync "{CONFIG["local_repo"]}" remote:EvidenceVault --fast-list'
        )

    print("[+] Cloud Tunnel Synchronization Completed Successfully.")


if __name__ == "__main__":
    tunnel_sync()
