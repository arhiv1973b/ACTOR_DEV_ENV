import json
from datetime import datetime, timedelta
import pytest

from rollback_fsm import (
    RollbackFSM,
    State
)


@pytest.fixture
def fsm(tmp_path, monkeypatch):
    state_file = tmp_path / "runtime-state.json"
    monkeypatch.setattr(
        "rollback_fsm.STATE_FILE",
        state_file
    )
    fsm = RollbackFSM()
    fsm.release_id = "release-1"
    return fsm


# --------------------------------------------------
# Initial state
# --------------------------------------------------

def test_initial_state(fsm):
    assert fsm.state == State.ACTIVE
    assert fsm.rollback_used is False


# --------------------------------------------------
# Alert transition
# --------------------------------------------------

def test_alert_moves_to_degraded(fsm):
    result = fsm.receive_alert("OCRAccuracyDrop")
    assert result["result"] == "accepted"
    assert fsm.state == State.DEGRADED


# --------------------------------------------------
# Duplicate alert
# --------------------------------------------------

def test_duplicate_alert_rejected(fsm):
    fsm.receive_alert("OCRAccuracyDrop")
    result = fsm.receive_alert("OCRAccuracyDrop")
    assert result["result"] == "duplicate"


# --------------------------------------------------
# Validation failure
# --------------------------------------------------

def test_validation_failure_returns_active(fsm):
    fsm.receive_alert("OCRAccuracyDrop")
    fsm.validate_alert(False)
    assert fsm.state == State.ACTIVE


# --------------------------------------------------
# Validation success
# --------------------------------------------------

def test_validation_success(fsm):
    fsm.receive_alert("MemoryLeak")
    fsm.validate_alert(True)
    assert fsm.state == State.VERIFIED


# --------------------------------------------------
# Rollback allowed
# --------------------------------------------------

def test_prepare_rollback(fsm, monkeypatch):
    fsm.receive_alert("A")
    fsm.validate_alert(True)
    monkeypatch.setattr(
        fsm,
        "checkpoint_exists",
        lambda: True
    )
    assert fsm.prepare_rollback()
    assert fsm.state == State.ROLLBACK_PENDING


# --------------------------------------------------
# Rollback denied without checkpoint
# --------------------------------------------------

def test_no_checkpoint_no_rollback(fsm, monkeypatch):
    fsm.receive_alert("A")
    fsm.validate_alert(True)
    monkeypatch.setattr(
        fsm,
        "checkpoint_exists",
        lambda: False
    )
    assert not fsm.prepare_rollback()


# --------------------------------------------------
# Success rollback
# --------------------------------------------------

def test_successful_rollback(fsm, monkeypatch):
    monkeypatch.setattr(
        fsm,
        "checkpoint_exists",
        lambda: True
    )
    monkeypatch.setattr(
        fsm,
        "perform_rollback",
        lambda: True
    )
    fsm.receive_alert("A")
    fsm.validate_alert(True)
    fsm.prepare_rollback()
    assert fsm.execute_rollback()
    assert fsm.state == State.COOLDOWN
    assert fsm.rollback_used


# --------------------------------------------------
# Failed rollback
# --------------------------------------------------

def test_failed_rollback(fsm, monkeypatch):
    monkeypatch.setattr(
        fsm,
        "checkpoint_exists",
        lambda: True
    )
    monkeypatch.setattr(
        fsm,
        "perform_rollback",
        lambda: False
    )
    fsm.receive_alert("A")
    fsm.validate_alert(True)
    fsm.prepare_rollback()
    result = fsm.execute_rollback()
    assert result is False
    assert fsm.state == State.ROLLBACK_FAILED


# --------------------------------------------------
# One rollback per release
# --------------------------------------------------

def test_second_rollback_blocked(fsm, monkeypatch):
    monkeypatch.setattr(
        fsm,
        "checkpoint_exists",
        lambda: True
    )
    monkeypatch.setattr(
        fsm,
        "perform_rollback",
        lambda: True
    )
    fsm.receive_alert("A")
    fsm.validate_alert(True)
    fsm.prepare_rollback()
    fsm.execute_rollback()
    assert not fsm.rollback_allowed()


# --------------------------------------------------
# Cooldown active
# --------------------------------------------------

def test_cooldown_active(fsm):
    fsm.cooldown_until = datetime.utcnow() + timedelta(hours=1)
    assert fsm.in_cooldown()


# --------------------------------------------------
# Cooldown expiry
# --------------------------------------------------

def test_cooldown_expired(fsm):
    fsm.state = State.COOLDOWN
    fsm.cooldown_until = datetime.utcnow() - timedelta(minutes=1)
    fsm.check_cooldown()
    assert fsm.state == State.RECOVERED


# --------------------------------------------------
# Recover to active
# --------------------------------------------------

def test_recover(fsm):
    fsm.state = State.RECOVERED
    fsm.recover()
    assert fsm.state == State.ACTIVE


# --------------------------------------------------
# Promotion allowed
# --------------------------------------------------

def test_promotion_allowed(fsm):
    assert fsm.promotion_allowed()


# --------------------------------------------------
# Promotion blocked after rollback
# --------------------------------------------------

def test_promotion_blocked_after_rollback(fsm):
    fsm.rollback_used = True
    assert not fsm.promotion_allowed()


# --------------------------------------------------
# Persistence save/load
# --------------------------------------------------

def test_persistence(tmp_path, monkeypatch):
    state_file = tmp_path / "runtime-state.json"
    monkeypatch.setattr(
        "rollback_fsm.STATE_FILE",
        state_file
    )
    fsm = RollbackFSM()
    fsm.state = State.DEGRADED
    fsm.release_id = "r42"
    fsm.rollback_used = True
    fsm.save()

    fsm2 = RollbackFSM()
    assert fsm2.state == State.DEGRADED
    assert fsm2.release_id == "r42"
    assert fsm2.rollback_used is True


# --------------------------------------------------
# Fingerprint stable
# --------------------------------------------------

def test_fingerprint_consistency(fsm):
    fp1 = fsm.fingerprint("OCRAccuracyDrop")
    fp2 = fsm.fingerprint("OCRAccuracyDrop")
    assert fp1 == fp2


# --------------------------------------------------
# Fingerprint unique
# --------------------------------------------------

def test_fingerprint_unique(fsm):
    fp1 = fsm.fingerprint("A")
    fp2 = fsm.fingerprint("B")
    assert fp1 != fp2
