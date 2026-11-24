#!/usr/bin/env python3
import tempfile
from pathlib import Path
import shutil
from rollback_fsm_bun import RollbackFSM, BackendExecResult, load_quarantine_cache

def test_run():
    tmp = Path(tempfile.mkdtemp())
    try:
        cache_path = tmp / "quarantine.json"
        env_fp = "win11-noavx-test"

        def mock_runner(backend: str, prompt: str) -> BackendExecResult:
            if "bun" in backend:
                return BackendExecResult(
                    exit_code=132,
                    stderr="CPU lacks AVX support. panic(main thread): Illegal instruction",
                )
            return BackendExecResult(
                exit_code=0,
                stdout=f"Success from {backend}",
            )

        fsm = RollbackFSM(
            runner=mock_runner,
            cache_path=cache_path,
            env_fingerprint=env_fp,
        )

        res = fsm.run(["bun_opencode", "python_backend"], "test prompt")
        assert res.ok is True
        assert res.selected_backend == "python_backend"
        assert res.quarantined_now is True
        print("✓ First run quarantine & fallback passed")

        cache_data = load_quarantine_cache(cache_path)
        assert cache_data[env_fp]["bun_opencode"]["status"] == "QUARANTINED"
        print("✓ Quarantine cache persistence passed")

        res2 = fsm.run(["bun_opencode", "python_backend"], "test prompt 2")
        assert res2.ok is True
        assert res2.selected_backend == "python_backend"
        assert res2.attempted_backends == ["python_backend"]
        print("✓ Cached quarantine fast-skip passed")

        print("\nAll RollbackFSM Bun Quarantine tests passed successfully!")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    test_run()
