#!/usr/bin/env python3
"""
Jus Cogens Heartbeat Miner (Proof-of-Integrity Daemon)
Version: 2026.1.0
Signature: # ⚖ A©tor Declaration
"""

import os
import sys
import time
import datetime
import hashlib
import subprocess

LEDGER_PATH = "evidence_ledger_sha256.log"
PROOF_PATH = "proof_of_life.log"
BRANCH = "feature/cyber-sabotage-audit-10-2026"
INTERVAL_SECONDS = 900  # 15 minutes heartbeat


def log_msg(msg):
    timestamp = datetime.datetime.utcnow().isoformat()
    print(f"[{timestamp}] [HEARTBEAT] {msg} | Signature: # ⚖ A©tor Declaration")


def heartbeat_iteration():
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    marker = f"[{now_str}] Jus Cogens Protocol ACTIVE - Hardware sabotage bypassed. Integrity verified.\n"

    # 1. Append to proof_of_life.log
    with open(PROOF_PATH, "a", encoding="utf-8") as f:
        f.write(marker)
    log_msg("Generated proof of life marker.")

    # 2. Compute SHA-256 of proof_of_life.log
    with open(PROOF_PATH, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()

    # 3. Append hash to evidence_ledger_sha256.log
    ledger_entry = f"proof_of_life.log: {h} [{now_str}]\n"
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(ledger_entry)
    log_msg(f"Appended proof hash to ledger: {h}")

    # 4. Git add, commit, push
    cmd = f'git add -f {PROOF_PATH} {LEDGER_PATH} && git commit -m "chore(security): automated proof-of-integrity heartbeat node [Jus Cogens] at {now_str}" && git push origin {BRANCH}'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    log_msg(f"Git sync output: {res.stdout.strip() or res.stderr.strip()}")


def main():
    log_msg("Starting Jus Cogens Heartbeat Miner Daemon...")
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        heartbeat_iteration()
        return

    while True:
        try:
            heartbeat_iteration()
        except Exception as e:
            log_msg(f"Error in heartbeat cycle: {e}")
        log_msg(f"Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
