#!/usr/bin/env python3
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class BackendExecResult:
    """Результат однократного запуска конкретного бэкенда."""
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


@dataclass
class FSMResult:
    """Итоговый результат работы FSM."""
    ok: bool
    final_state: str
    selected_backend: str | None = None
    attempted_backends: list[str] = field(default_factory=list)
    quarantined_now: bool = False
    rollback_count: int = 0
    failure_reason: str | None = None
    output: str = ""


def load_quarantine_cache(cache_path: Path) -> dict[str, Any]:
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_quarantine_cache_atomic(cache_path: Path, data: dict[str, Any]) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = cache_path.with_name(f".{cache_path.name}.tmp")
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    with open(tmp_path, "wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, cache_path)


class RollbackFSM:
    """Конечный автомат откатов с карантином Bun при фатальном сбое рантайма."""

    FATAL_RUNTIME_CODES = {132, 139}  # 132 = 128 + 4 (SIGILL), 139 = 128 + 11 (SIGSEGV)
    FATAL_STDERR_MARKERS = (
        "illegal instruction",
        "sigill",
        "cpu lacks avx",
        "avx support",
    )

    def __init__(
        self,
        runner: Callable[[str, str], BackendExecResult],
        cache_path: Path,
        env_fingerprint: str,
        bun_backends: set[str] | None = None,
        rollback_cleanup: Callable[[str], None] | None = None,
    ) -> None:
        self.runner = runner
        self.cache_path = cache_path
        self.env_fingerprint = env_fingerprint
        self.bun_backends = bun_backends or {"bun", "bun_opencode", "opencode_bun"}
        self.rollback_cleanup = rollback_cleanup

    def _is_bun_backend(self, backend: str) -> bool:
        return backend in self.bun_backends or "bun" in backend.lower()

    def _is_bun_quarantined(self, cache: dict[str, Any], backend: str) -> bool:
        if not self._is_bun_backend(backend):
            return False
        env_entry = cache.get(self.env_fingerprint)
        if not isinstance(env_entry, dict):
            return False
        bun_entry = env_entry.get(backend)
        return isinstance(bun_entry, dict) and bun_entry.get("status") == "QUARANTINED"

    def _classify_failure(self, backend: str, exec_res: BackendExecResult) -> str:
        """Возвращает 'RUNTIME_FATAL' при SIGILL/сбое инструкций или 'TRANSIENT' для прочих сбоев."""
        combined_err = f"{exec_res.stderr}\n{exec_res.stdout}".lower()
        if exec_res.exit_code in self.FATAL_RUNTIME_CODES:
            return "RUNTIME_FATAL"
        if any(marker in combined_err for marker in self.FATAL_STDERR_MARKERS):
            return "RUNTIME_FATAL"
        return "TRANSIENT"

    def _quarantine_bun(
        self,
        cache: dict[str, Any],
        backend: str,
        reason: str,
    ) -> bool:
        """Фиксирует карантин Bun в кэше для текущего env_fingerprint."""
        if not self._is_bun_backend(backend):
            return False
        env_entry = cache.setdefault(self.env_fingerprint, {})
        if not isinstance(env_entry, dict):
            env_entry = {}
            cache[self.env_fingerprint] = env_entry

        env_entry[backend] = {
            "status": "QUARANTINED",
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        save_quarantine_cache_atomic(self.cache_path, cache)
        return True

    def run(self, backends: list[str], prompt: str) -> FSMResult:
        state = "INIT"
        cache = load_quarantine_cache(self.cache_path)
        attempted: list[str] = []
        rollback_count = 0
        quarantined_now = False
        last_reason: str | None = None

        if not backends:
            state = "ABORT"
            return FSMResult(
                ok=False,
                final_state=state,
                attempted_backends=attempted,
                quarantined_now=quarantined_now,
                rollback_count=rollback_count,
                failure_reason="empty_backend_list",
                output="",
            )

        queue = list(backends)
        state = "SELECT_BACKEND"

        while queue:
            backend = queue.pop(0)

            # Быстрый пропуск по кэшу карантина до запуска процесса
            if self._is_bun_quarantined(cache, backend):
                last_reason = f"cached_quarantine:{backend}"
                continue

            state = "RUNNING"
            attempted.append(backend)
            exec_res = self.runner(backend, prompt)

            if exec_res.exit_code == 0 and not exec_res.timed_out:
                state = "COMMIT"
                output_text = exec_res.stdout
                state = "DONE"
                return FSMResult(
                    ok=True,
                    final_state=state,
                    selected_backend=backend,
                    attempted_backends=attempted,
                    quarantined_now=quarantined_now,
                    rollback_count=rollback_count,
                    failure_reason=None,
                    output=output_text,
                )

            state = "CLASSIFY_FAILURE"
            failure_kind = self._classify_failure(backend, exec_res)
            detail = (
                "timeout"
                if exec_res.timed_out
                else f"exit_code={exec_res.exit_code}"
            )
            last_reason = f"{failure_kind}:{backend}({detail})"

            if failure_kind == "RUNTIME_FATAL" and self._is_bun_backend(backend):
                state = "QUARANTINE_BUN"
                if self._quarantine_bun(cache, backend, last_reason):
                    quarantined_now = True

            state = "ROLLBACK"
            rollback_count += 1
            if self.rollback_cleanup is not None:
                self.rollback_cleanup(backend)
            state = "SELECT_BACKEND"

        state = "ABORT"
        return FSMResult(
            ok=False,
            final_state=state,
            selected_backend=None,
            attempted_backends=attempted,
            quarantined_now=quarantined_now,
            rollback_count=rollback_count,
            failure_reason=last_reason or "all_backends_failed",
            output="",
        )
