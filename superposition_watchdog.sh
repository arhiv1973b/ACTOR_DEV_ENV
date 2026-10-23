#!/usr/bin/env bash
# Jus Cogens Self-Healing Watchdog (Linux/Mac)
# Signature: # ⚖ A©tor Declaration

SCRIPT_NAME="jus_cogens_heartbeat.py"
LOG_FILE="heartbeat_sys.log"

while true; do
    if ! pgrep -f "$SCRIPT_NAME" > /dev/null; then
        echo "[WATCHDOG] Heartbeat miner down! Restarting..."
        nohup python3 "$SCRIPT_NAME" > "$LOG_FILE" 2>&1 &
    fi
    sleep 60
done
