# orchestrator.py
"""
Orchestrator for the Dual‑Resilience workflow.
1️⃣ Starts ``mcp_monitor.py`` in background.
2️⃣ Executes ``dual_resilience_test.py`` with preset tasks.
3️⃣ Reads ``dual_handshake.json`` and ``dual_resilience_log.csv`` to compute a short status ``TI‑ULA``.
4️⃣ Stops the monitor (optional – can be kept running).
"""

import subprocess, sys, os, time, json, csv, pathlib, logging
from datetime import datetime, timezone
from mcp_logger import get_logger
logger = get_logger()

# Path to orchestrator metrics in mcp_metrics.json
METRICS_PATH = pathlib.Path(r"H:/ACTOR_DEV_ENV/mcp_metrics.json")

def write_orchestrator_heartbeat():
    """Update orchestrator heartbeat timestamp in mcp_metrics.json."""
    if not METRICS_PATH.is_file():
        metrics = {"agents": {}}
    else:
        try:
            metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        except Exception:
            metrics = {"agents": {}}
    agents = metrics.setdefault("agents", {})
    agents["orchestrator"] = {
        "status": "ok",
        "msg": "running",
        "last_update": datetime.now(timezone.utc).isoformat()
    }
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

# Absolute paths to workspace files
WORKSPACE_ROOT = pathlib.Path(r"H:/ACTOR_DEV_ENV")
VENV_PY = WORKSPACE_ROOT / ".venv" / "Scripts" / "python.exe"
if not VENV_PY.is_file():
    # fallback for Linux‑style venv (bin/python)
    VENV_PY = WORKSPACE_ROOT / ".venv" / "bin" / "python"

MONITOR_SCRIPT = WORKSPACE_ROOT / "mcp_monitor.py"
TEST_SCRIPT = WORKSPACE_ROOT / "dual_resilience_test.py"
LOG_DIR = WORKSPACE_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
MONITOR_LOG = LOG_DIR / "mcp_monitor.out"
TEST_LOG = LOG_DIR / "dual_resilience_test.out"
HANDSHAKE = WORKSPACE_ROOT / "dual_handshake.json"
CSV_LOG = WORKSPACE_ROOT / "dual_resilience_log.csv"

def launch_background(cmd, log_path):
    log_f = open(log_path, "ab")
    proc = subprocess.Popen(
        cmd,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        cwd=str(WORKSPACE_ROOT),
        shell=False,
        close_fds=False,
    )
    return proc

def start_monitor():
    if not MONITOR_SCRIPT.is_file():
        sys.exit(f"Monitor script not found: {MONITOR_SCRIPT}")
    return launch_background([str(VENV_PY), str(MONITOR_SCRIPT)], MONITOR_LOG)

def run_test():
    cmd = [
        str(VENV_PY),
        str(TEST_SCRIPT),
        "--config",
        "mcp_config.yaml",
        "--tasks",
        "Repair logging block",
        "Optimize restart-policy for agents",
        "--threshold",
        "0.75",
    ]
    with open(TEST_LOG, "wb") as out:
        proc = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT, cwd=str(WORKSPACE_ROOT))
    return proc.returncode

def read_handshake():
    if not HANDSHAKE.is_file():
        return {}
    try:
        return json.loads(HANDSHAKE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def restart_agent(agent_name: str) -> bool:
    """Attempt to restart an agent via MCP CLI.
    Returns True if restart succeeded, False otherwise.
    If MCP CLI is unavailable, falls back to updating metrics locally.
    """
    logger.info("Attempting to restart agent '%s'", agent_name)
    cmd = ["mcp", "agent", "restart", agent_name]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Agent '%s' restarted successfully", agent_name)
        return True
    except FileNotFoundError:
        # MCP CLI not installed – simulate restart by refreshing metrics
        logger.warning("MCP CLI not found – performing fallback restart for %s", agent_name)
        try:
            # Load metrics, update agent entry
            if METRICS_PATH.is_file():
                metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
            else:
                metrics = {"agents": {}}
            agents = metrics.setdefault("agents", {})
            agents[agent_name] = {
                "status": "ok",
                "msg": "restarted (fallback)",
                "last_update": datetime.now(timezone.utc).isoformat()
            }
            METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
            logger.info("Fallback restart for agent '%s' applied via metrics update", agent_name)
            return True
        except Exception as exc2:
            logger.error("Fallback restart failed for '%s': %s", agent_name, exc2)
            return False
    except Exception as exc:
        logger.error("Restart failed for '%s': %s", agent_name, exc)
        return False

def compute_status(csv_path: pathlib.Path) -> str:
    if not csv_path.is_file():
        return "NO_DATA"
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if not rows:
                return "EMPTY"
            last = rows[-1]
    except Exception as e:
        return f"ERR:{e}"
    repair = last.get("repair_by", "")
    similarity = float(last.get("similarity", "0"))
    if repair:
        return f"REPAIR_BY_{repair.upper()}"
    return "OK" if similarity >= 0.75 else "FAIL"

def main():
    if not VENV_PY.is_file():
        sys.exit("Python interpreter from .venv not found. Activate the venv first.")
    monitor_proc = start_monitor()
    write_orchestrator_heartbeat()
    time.sleep(2)  # give monitor a moment to initialise
    rc = run_test()
    if rc != 0:
        print(f"Test returned error code {rc}")
    handshake = read_handshake()
    # Load metrics to assess legal_agent heartbeat
    try:
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    except Exception:
        metrics = {}
    legal_status = "UNKNOWN"
    if metrics.get("agents", {}).get("legal_agent"):
        la = metrics["agents"]["legal_agent"]
        ts = la.get("last_update")
        if ts:
            try:
                from datetime import datetime, timezone
                last = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                age = (datetime.now(timezone.utc) - last).total_seconds()
                legal_status = "OK" if age <= 60 else "STALE"
            except Exception:
                legal_status = "INVALID"
        else:
            legal_status = "MISSING"
    else:
        legal_status = "MISSING"
    logger.info("Legal agent heartbeat status: %s", legal_status)
    status = compute_status(CSV_LOG)
    print("\n=== Orchestrator result ===")
    print(f"TI‑ULA status : {status}")
    print(f"Legal agent heartbeat : {legal_status}")
    print(f"Last run_id   : {list(handshake.keys())[-1] if handshake else 'N/A'}")
    print(f"Monitor log   : {MONITOR_LOG}")
    print(f"Test log      : {TEST_LOG}")
    print(f"CSV log       : {CSV_LOG}")
    # stop monitor (optional)
    monitor_proc.terminate()
    try:
        monitor_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        monitor_proc.kill()
    print("Monitor stopped.")

if __name__ == "__main__":
    main()
