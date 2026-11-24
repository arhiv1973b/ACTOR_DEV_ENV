#!/usr/bin/env python3
import sys
from pathlib import Path
import tempfile
import shutil

# Import tests and module
sys.path.insert(0, str(Path(__file__).parent))
import rollback_fsm
from rollback_fsm import RollbackFSM, State

class MockTmpPath(Path):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, tempfile.mkdtemp())

def run_all_tests():
    print("Running RollbackFSM unit tests...")
    
    # Test 1: Initial state
    tmp1 = Path(tempfile.mkdtemp())
    try:
        fsm = RollbackFSM()
        assert fsm.state == State.ACTIVE
        assert fsm.rollback_used is False
        print("✓ test_initial_state passed")
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)

    # Test 2: Alert moves to degraded
    tmp2 = Path(tempfile.mkdtemp())
    try:
        rollback_fsm.STATE_FILE = tmp2 / "runtime-state.json"
        fsm = RollbackFSM()
        res = fsm.receive_alert("OCRAccuracyDrop")
        assert res["result"] == "accepted"
        assert fsm.state == State.DEGRADED
        print("✓ test_alert_moves_to_degraded passed")
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    # Test 3: Duplicate alert rejected
    tmp3 = Path(tempfile.mkdtemp())
    try:
        rollback_fsm.STATE_FILE = tmp3 / "runtime-state.json"
        fsm = RollbackFSM()
        fsm.receive_alert("OCRAccuracyDrop")
        res = fsm.receive_alert("OCRAccuracyDrop")
        assert res["result"] == "duplicate"
        print("✓ test_duplicate_alert_rejected passed")
    finally:
        shutil.rmtree(tmp3, ignore_errors=True)

    # Test 4: Validation failure returns active
    tmp4 = Path(tempfile.mkdtemp())
    try:
        rollback_fsm.STATE_FILE = tmp4 / "runtime-state.json"
        fsm = RollbackFSM()
        fsm.receive_alert("OCRAccuracyDrop")
        fsm.validate_alert(False)
        assert fsm.state == State.ACTIVE
        print("✓ test_validation_failure_returns_active passed")
    finally:
        shutil.rmtree(tmp4, ignore_errors=True)

    # Test 5: Validation success
    tmp5 = Path(tempfile.mkdtemp())
    try:
        rollback_fsm.STATE_FILE = tmp5 / "runtime-state.json"
        fsm = RollbackFSM()
        fsm.receive_alert("MemoryLeak")
        fsm.validate_alert(True)
        assert fsm.state == State.VERIFIED
        print("✓ test_validation_success passed")
    finally:
        shutil.rmtree(tmp5, ignore_errors=True)

    # Test 6: Persistence
    tmp6 = Path(tempfile.mkdtemp())
    try:
        rollback_fsm.STATE_FILE = tmp6 / "runtime-state.json"
        fsm = RollbackFSM()
        fsm.state = State.DEGRADED
        fsm.release_id = "r42"
        fsm.rollback_used = True
        fsm.save()

        fsm2 = RollbackFSM()
        assert fsm2.state == State.DEGRADED
        assert fsm2.release_id == "r42"
        assert fsm2.rollback_used is True
        print("✓ test_persistence passed")
    finally:
        shutil.rmtree(tmp6, ignore_errors=True)

    print("\nAll RollbackFSM unit tests passed successfully!")

if __name__ == "__main__":
    run_all_tests()
