#!/usr/bin/env python3
"""Подпроцессный ранер с декодированием UTF-8 и таймаутами для RollbackFSM."""

from collections.abc import Callable
from pathlib import Path
import subprocess
from typing import Any

from rollback_fsm_bun import BackendExecResult, FSMResult, RollbackFSM, build_env_fingerprint


def _decode_stream(data: bytes | str | None) -> str:
    """Декодирует вывод подпроцесса в UTF-8 без падения при невалидных байтах."""
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    return data.decode("utf-8", errors="replace")


def make_subprocess_runner(
    command_builders: dict[str, Callable[[str], list[str]]],
    timeout_sec: float = 120.0,
    cwd: Path | str | None = None,
) -> Callable[[str, str], BackendExecResult]:
    """Создаёт runner(backend, prompt) -> BackendExecResult с таймаутом и UTF-8."""

    def runner(backend: str, prompt: str) -> BackendExecResult:
        builder = command_builders.get(backend)
        if builder is None:
            return BackendExecResult(
                exit_code=2,
                stdout="",
                stderr=f"unknown_backend:{backend}",
                timed_out=False,
            )

        cmd = builder(prompt)
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd is not None else None,
                capture_output=True,
                timeout=timeout_sec,
                check=False,
            )
            return BackendExecResult(
                exit_code=int(proc.returncode),
                stdout=_decode_stream(proc.stdout),
                stderr=_decode_stream(proc.stderr),
                timed_out=False,
            )
        except subprocess.TimeoutExpired as exc:
            return BackendExecResult(
                exit_code=124,
                stdout=_decode_stream(exc.stdout),
                stderr=_decode_stream(exc.stderr) or f"timeout_after_{timeout_sec}s",
                timed_out=True,
            )
        except OSError as exc:
            return BackendExecResult(
                exit_code=126,
                stdout="",
                stderr=f"os_error:{exc}",
                timed_out=False,
            )

    return runner


def run_with_fallback(
    prompt: str,
    cache_path: Path,
    work_dir: Path,
    bun_version: str | None = "1.3.10",
) -> FSMResult:
    """Запускает цепочку бэкендов с карантином Bun при SIGILL (код 132) и откатом на Ollama."""
    command_builders: dict[str, Callable[[str], list[str]]] = {
        "bun_opencode": lambda p: ["opencode", "run", p],
        "ollama": lambda p: ["ollama", "run", "qwen2.5:3b", p],
    }

    env_fp = build_env_fingerprint(
        bun_version=bun_version,
        extra_tags={"orchestrator": "ai_cli_wrapper"},
    )
    runner = make_subprocess_runner(
        command_builders=command_builders,
        timeout_sec=120.0,
        cwd=work_dir,
    )
    fsm = RollbackFSM(
        runner=runner,
        cache_path=cache_path,
        env_fingerprint=env_fp,
    )
    return fsm.run(backends=["bun_opencode", "ollama"], prompt=prompt)
