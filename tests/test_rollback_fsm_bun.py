#!/usr/bin/env python3
import pytest
from pathlib import Path
from rollback_fsm_bun import RollbackFSM, BackendExecResult, load_quarantine_cache


def test_bun_quarantine_on_sigill(tmp_path):
    cache_path = tmp_path / "quarantine.json"
    env_fp = "win11-noavx-test"

    # Runner: bun fails with exit code 132 (SIGILL / illegal instruction), python succeeds
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

    # First run: bun fails and gets quarantined, falls back to python
    res = fsm.run(["bun_opencode", "python_backend"], "test prompt")
    assert res.ok is True
    assert res.selected_backend == "python_backend"
    assert res.quarantined_now is True
    assert res.attempted_backends == ["bun_opencode", "python_backend"]

    # Verify cache has bun_opencode quarantined
    cache_data = load_quarantine_cache(cache_path)
    assert cache_data[env_fp]["bun_opencode"]["status"] == "QUARANTINED"

    # Second run: bun_opencode should be skipped immediately via cached quarantine
    res2 = fsm.run(["bun_opencode", "python_backend"], "test prompt 2")
    assert res2.ok is True
    assert res2.selected_backend == "python_backend"
    # bun_opencode was skipped entirely because of cache
    assert res2.attempted_backends == ["python_backend"]
