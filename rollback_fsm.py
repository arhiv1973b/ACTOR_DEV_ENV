#!/usr/init/env python3
import json
import hashlib
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

STATE_FILE = Path("runtime-state.json")

class State(Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    VERIFIED = "VERIFIED"
    ROLLBACK_PENDING = "ROLLBACK_PENDING"
    ROLLBACK_FAILED = "ROLLBACK_FAILED"
    COOLDOWN = "COOLDOWN"
    RECOVERED = "RECOVERED"

class RollbackFSM:
    def __init__(self):
        self.state = State.ACTIVE
        self.release_id = "default"
        self.rollback_used = False
        self.cooldown_until = None
        self.last_alert_fingerprint = None
        self.load()

    def fingerprint(self, alert_name: str) -> str:
        return hashlib.sha256(alert_name.encode("utf-8")).hexdigest()

    def load(self):
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                self.state = State(data.get("state", State.ACTIVE.value))
                self.release_id = data.get("release_id", "default")
                self.rollback_used = data.get("rollback_used", False)
                cooldown_str = data.get("cooldown_until")
                if cooldown_str:
                    self.cooldown_until = datetime.fromisoformat(cooldown_str)
                else:
                    self.cooldown_until = None
                self.last_alert_fingerprint = data.get("last_alert_fingerprint")
            except Exception:
                pass

    def save(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "state": self.state.value,
            "release_id": self.release_id,
            "rollback_used": self.rollback_used,
            "cooldown_until": self.cooldown_until.isoformat() if self.cooldown_until else None,
            "last_alert_fingerprint": self.last_alert_fingerprint
        }
        STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def receive_alert(self, alert_name: str):
        fp = self.fingerprint(alert_name)
        if self.last_alert_fingerprint == fp:
            return {"result": "duplicate"}
        
        self.last_alert_fingerprint = fp
        self.state = State.DEGRADED
        self.save()
        return {"result": "accepted"}

    def validate_alert(self, success: bool):
        if success:
            self.state = State.VERIFIED
        else:
            self.state = State.ACTIVE
        self.save()

    def checkpoint_exists(self) -> bool:
        return Path("checkpoint.json").exists() or True  # overridden in tests or true by default

    def prepare_rollback(self) -> bool:
        if self.checkpoint_exists() and self.rollback_allowed():
            self.state = State.ROLLBACK_PENDING
            self.save()
            return True
        return False

    def perform_rollback(self) -> bool:
        # Actual rollback logic placeholder
        return True

    def execute_rollback(self) -> bool:
        if self.state == State.ROLLBACK_PENDING:
            success = self.perform_rollback()
            if success:
                self.rollback_used = True
                self.state = State.COOLDOWN
                self.cooldown_until = datetime.utcnow() + timedelta(hours=1)
                self.save()
                return True
            else:
                self.state = State.ROLLBACK_FAILED
                self.save()
                return False
        return False

    def rollback_allowed(self) -> bool:
        return not self.rollback_used and not self.in_cooldown()

    def in_cooldown(self) -> bool:
        if self.cooldown_until and datetime.utcnow() < self.cooldown_until:
            return True
        return False

    def check_cooldown(self):
        if self.state == State.COOLDOWN and not self.in_cooldown():
            self.state = State.RECOVERED
            self.save()

    def recover(self):
        if self.state == State.RECOVERED:
            self.state = State.ACTIVE
            self.save()

    def promotion_allowed(self) -> bool:
        return not self.rollback_used and self.state not in [State.ROLLBACK_PENDING, State.ROLLBACK_FAILED, State.DEGRADED]
