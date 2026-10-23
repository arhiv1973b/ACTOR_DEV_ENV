#!/usr/bin/env python3
import sys
import json
import os
import time
from datetime import datetime

AUDIT_DIR = "/app/.audit"
AUDIT_FILE = os.path.join(AUDIT_DIR, "events.json")

def generate_telemetry():
    if not os.path.exists(AUDIT_DIR):
        os.makedirs(AUDIT_DIR, exist_ok=True)
    
    events = [
        {
            "event_id": "EVT-001",
            "type": "file.access",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {"path": "/etc/passwd", "action": "read", "user": "appuser"}
        },
        {
            "event_id": "EVT-002",
            "type": "process.exec",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {"command": "ls -la /app", "user": "appuser"}
        },
        {
            "event_id": "EVT-003",
            "type": "network.connection",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {"destination": "127.0.0.1", "port": 11434}
        }
    ]
    
    with open(AUDIT_FILE, "w") as f:
        json.dump(events, f, indent=2)
    
    print(f"[TI-ULA] Generated {len(events)} telemetry events in {AUDIT_FILE}")

if __name__ == "__main__":
    print(f"[ACTOR] Started TI-ULA Node 1 telemetry service")
    generate_telemetry()
    print("[ACTOR] Sleeping for 60 seconds to allow host audit...")
    time.sleep(60)
    print("[ACTOR] Telemetry service shutting down.")
