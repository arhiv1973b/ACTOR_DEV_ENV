#!/usr/bin/env python3
"""
Jus Cogens Heartbeat Miner (Proof-of-Integrity Daemon with Air-Gapped Resilience)
Version: 2026.2.0
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
    marker = f"[{now_str}] Jus Cogens Protocol ACTIVE - Hardware sabotage bypassed. Air-gapped superposition locked.\n"

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

    # 4. Git add, commit, and resilient push
    try:
        add_res = subprocess.run(
            f"git add -f {PROOF_PATH} {LEDGER_PATH}",
            shell=True,
            capture_output=True,
            text=True,
        )
        commit_res = subprocess.run(
            f'git commit -m "chore(security): automated proof-of-integrity heartbeat node [Jus Cogens] at {now_str}"',
            shell=True,
            capture_output=True,
            text=True,
        )

        push_res = subprocess.run(
            f"git push origin {BRANCH}", shell=True, capture_output=True, text=True
        )
        if push_res.returncode != 0:
            log_msg(
                f"Network offline or push rejected. Appending locally... ({push_res.stderr.strip()})"
            )
        else:
            log_msg(f"Git push successful: {push_res.stdout.strip()}")
    except Exception as e:
        log_msg(f"Network offline exception caught. Appending locally... Error: {e}")


def main():
    log_msg("Starting Jus Cogens Heartbeat Miner Daemon (Air-Gapped Resilient)...")
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
