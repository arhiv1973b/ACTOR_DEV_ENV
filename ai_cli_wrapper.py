#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write_bytes(target: Path, data: bytes) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    with open(tmp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, target)
    return sha256_bytes(data)


def atomic_write_json(target: Path, payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    atomic_write_bytes(target, raw)


def load_checkpoint(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"status": "init", "attempts_total": 0, "last_sha256": None}


def run_with_retries(
    cmd: list[str],
    out_path: Path,
    state_path: Path,
    max_attempts: int = 5,
    base_delay: float = 1.5,
    max_delay: float = 30.0,
    timeout_sec: float = 60.0,
    resume: bool = False,
) -> int:
    state = load_checkpoint(state_path) if resume else {
        "status": "running",
        "attempts_total": 0,
        "last_sha256": None,
    }

    if resume and state.get("status") == "completed" and out_path.exists():
        actual_hash = sha256_bytes(out_path.read_bytes())
        if state.get("last_sha256") == actual_hash:
            print(f"[SKIP] Уже завершено по чекпоинту (sha256={actual_hash[:12]}...)")
            return 0

    for attempt in range(1, max_attempts + 1):
        state["attempts_total"] = state.get("attempts_total", 0) + 1
        state["status"] = "attempting"
        state["current_attempt"] = attempt
        state["updated_at"] = time.time()
        atomic_write_json(state_path, state)

        started = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_sec,
            )
            elapsed = round(time.monotonic() - started, 2)

            if proc.returncode == 0 and proc.stdout.strip():
                stdout_bytes = proc.stdout.encode("utf-8")
                digest = atomic_write_bytes(out_path, stdout_bytes)

                state.update({
                    "status": "completed",
                    "returncode": 0,
                    "elapsed_sec": elapsed,
                    "last_sha256": digest,
                    "output_file": str(out_path),
                    "hypothesis": None,
                    "updated_at": time.time(),
                })
                atomic_write_json(state_path, state)
                print(f"[OK] Попытка {attempt}/{max_attempts} за {elapsed}s, sha256={digest[:12]}...")
                return 0

            # Факт неуспешного завершения или пустого stdout
            stderr_tail = (proc.stderr or "").strip()[-400:]
            hypothesis = (
                "Пустой stdout при коде 0"
                if proc.returncode == 0
                else "Ненулевой код возврата CLI (возможна перегрузка/лимит/ошибка аргументов)"
            )
            state.update({
                "status": "retry_scheduled",
                "returncode": proc.returncode,
                "elapsed_sec": elapsed,
                "stderr_tail": stderr_tail,
                "hypothesis": hypothesis,
                "updated_at": time.time(),
            })
            atomic_write_json(state_path, state)
            print(f"[WARN] Попытка {attempt}/{max_attempts} не удалась (rc={proc.returncode}, {elapsed}s)")

        except subprocess.TimeoutExpired:
            elapsed = round(time.monotonic() - started, 2)
            state.update({
                "status": "retry_scheduled",
                "returncode": None,
                "elapsed_sec": elapsed,
                "hypothesis": "Превышен таймаут выполнения команды/потока",
                "updated_at": time.time(),
            })
            atomic_write_json(state_path, state)
            print(f"[TIMEOUT] Попытка {attempt}/{max_attempts} превысила {timeout_sec}s")

        if attempt < max_attempts:
            exp = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0.0, min(1.0, exp * 0.25))
            sleep_sec = round(exp + jitter, 2)
            print(f"[BACKOFF] Пауза {sleep_sec}s перед следующей попыткой...")
            time.sleep(sleep_sec)

    state["status"] = "failed"
    state["updated_at"] = time.time()
    atomic_write_json(state_path, state)
    print(f"[FAIL] Исчерпаны все {max_attempts} попыток. См. чекпоинт: {state_path}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Минимальная надежная CLI-обертка")
    parser.add_argument("--out", required=True, type=Path, help="Путь к итоговому файлу результата")
    parser.add_argument("--state", required=True, type=Path, help="Путь к JSON-файлу чекпоинта")
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--base-delay", type=float, default=1.5)
    parser.add_argument("--max-delay", type=float, default=30.0)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--resume", action="store_true", help="Пропустить выполнение, если чекпоинт и SHA-256 актуальны")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Команда CLI после '--'")
    args = parser.parse_args()

    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        print("Укажите команду после '--'", file=sys.stderr)
        return 2

    return run_with_retries(
        cmd=cmd,
        out_path=args.out,
        state_path=args.state,
        max_attempts=args.max_attempts,
        base_delay=args.base_delay,
        max_delay=args.max_delay,
        timeout_sec=args.timeout,
        resume=args.resume,
    )


if __name__ == "__main__":
    raise SystemExit(main())
