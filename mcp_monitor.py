# mcp_monitor.py
"""Advanced MCP monitor with heartbeat tracking, restart limits, and config validation.

Features:
- Periodically reads `mcp_metrics.json`.
- Detects missing or stale metric timestamps (heartbeat > threshold).
- Validates `mcp_config.yaml` (required keys and expected types).
- Enforces a restart policy: max 3 restarts per agent within a 5‑minute window.
- Logs critical failures and exits with status 1 on fatal errors.
"""

# ── IMPORTS ─────────────────────────────────────────────────────────────────────
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from mcp_logger import get_logger

# ── LOGGING CONFIG ───────────────────────────────────────────────────────────
logging.basicConfig(
    filename='logs/mcp_monitor.out',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# ── CONSTANTS & GLOBAL STATE ─────────────────────────────────────────────────
WORKSPACE_ROOT = Path(r"H:/ACTOR_DEV_ENV")
METRICS_PATH = WORKSPACE_ROOT / "mcp_metrics.json"
CONFIG_PATH = WORKSPACE_ROOT / "mcp_config.yaml"
HEARTBEAT_FILE = WORKSPACE_ROOT / "logs" / "mcp_heartbeat_last.txt"
DEFAULT_INTERVAL = 30  # seconds (fallback if config missing or invalid)
HEARTBEAT_STALE_FACTOR = 2  # multiplier for interval to consider stale
RESTART_LIMIT = 3                # max restarts
RESTART_WINDOW = timedelta(minutes=5)  # time window for restart limit

logger = get_logger()

# ── CONFIG LOADER & VALIDATOR ─────────────────────────────────────────────────
def load_and_validate_config() -> dict:
    """Load `mcp_config.yaml` and validate required structure.
    Returns an empty dict on failure (monitor will fall back to defaults).
    """
    try:
        import yaml
    except ImportError:
        logger.error("yaml library not installed – cannot load config")
        return {}
    if not CONFIG_PATH.is_file():
        logger.warning("Config file not found: %s", CONFIG_PATH)
        return {}
    try:
        raw_cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        logger.error("Failed to parse config yaml: %s", exc)
        return {}

    # Expected keys and types
    valid = True
    monitoring = raw_cfg.get("monitoring", {})
    if "heartbeat_interval_seconds" in monitoring:
        if not isinstance(monitoring["heartbeat_interval_seconds"], (int, float)):
            logger.error("heartbeat_interval_seconds must be numeric")
            valid = False
    else:
        logger.info("heartbeat_interval_seconds not set – using default")
    if "auto_repair" in monitoring:
        if not isinstance(monitoring["auto_repair"], bool):
            logger.error("auto_repair must be boolean")
            valid = False
    # Additional validation can be added here
    if not valid:
        logger.error("Configuration validation failed – falling back to defaults")
        return {}
    return raw_cfg

# ── METRICS READER ───────────────────────────────────────────────────────────
def read_metrics() -> dict:
    if not METRICS_PATH.is_file():
        return {}
    try:
        return json.load(METRICS_PATH.open('r', encoding='utf-8'))
    except Exception as exc:
        logger.error("Failed to read metrics file: %s", exc)
        return {}

# ── HEARTBEAT HANDLING (file based) ─────────────────────────────────────────────
def update_heartbeat_file():
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()
    HEARTBEAT_FILE.write_text(now_iso, encoding='utf-8')

def heartbeat_is_fresh(interval: int) -> bool:
    if not HEARTBEAT_FILE.is_file():
        logger.critical("Heartbeat file missing – monitor may be stuck")
        return False
    try:
        ts = HEARTBEAT_FILE.read_text(encoding='utf-8').strip()
        last = datetime.fromisoformat(ts)
    except Exception as exc:
        logger.error("Unable to parse heartbeat timestamp: %s", exc)
        return False
    delta = (datetime.now(timezone.utc) - last).total_seconds()
    if delta > interval * HEARTBEAT_STALE_FACTOR:
        logger.critical("Heartbeat stale (%.1f s) – possible monitor hang", delta)
        return False
    return True

# ── RESTART POLICY TRACKER ─────────────────────────────────────────────────────
class RestartTracker:
    def __init__(self):
        # For each agent keep a deque of recent restart timestamps
        self.history: dict[str, deque[datetime]] = defaultdict(deque)

    def record(self, agent: str) -> bool:
        """Record a restart attempt. Returns True if the limit is exceeded."""
        now = datetime.now(timezone.utc)
        dq = self.history[agent]
        dq.append(now)
        # Remove entries older than RESTART_WINDOW
        while dq and now - dq[0] > RESTART_WINDOW:
            dq.popleft()
        if len(dq) > RESTART_LIMIT:
            logger.error("Agent %s exceeded restart limit (%d within %s)", agent, RESTART_LIMIT, RESTART_WINDOW)
            return True
        return False

restart_tracker = RestartTracker()

# ── AGENT RESTART & HEARTBEAT CHECK ───────────────────────────────────────────────
def restart_agent(agent_name: str) -> bool:
    """Attempt to restart an agent via MCP CLI.
    Returns True if restart succeeded, False otherwise.
    """
    logger.info("Attempting to restart agent '%s'", agent_name)
    cmd = ["mcp", "agent", "restart", agent_name]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Agent '%s' restarted successfully", agent_name)
        return True
    except Exception as exc:
        logger.error("Restart failed for '%s': %s", agent_name, exc)
        return False

def check_agent_heartbeat(agent_name: str, agent_data: dict, interval: int) -> bool:
    """Return True if the agent's own heartbeat (timestamp field) is fresh.
    Expected format: agent_data may contain a 'last_update' ISO timestamp.
    If missing or stale, return False.
    """
    ts_str = agent_data.get('last_update')
    if not ts_str:
        logger.warning("Agent %s reports no last_update timestamp", agent_name)
        return False
    try:
        ts = datetime.fromisoformat(ts_str)
    except Exception as exc:
        logger.error("Invalid timestamp for agent %s: %s", agent_name, exc)
        return False
    delta = (datetime.now(timezone.utc) - ts).total_seconds()
    if delta > interval * HEARTBEAT_STALE_FACTOR:
        logger.warning("Agent %s heartbeat stale (%.1f s)", agent_name, delta)
        return False
    return True

# ── MAIN LOOP ───────────────────────────────────────────────────────────────────
def monitor_loop():
    cfg = load_and_validate_config()
    interval = cfg.get("monitoring", {}).get("heartbeat_interval_seconds", DEFAULT_INTERVAL)
    logger.info("MCP monitor started (interval=%s s)", interval)
    logging.info("MCP Monitor: initialization complete")
    print("Monitor started")

    # Ensure at least one metrics record exists
    if not METRICS_PATH.is_file():
        dummy = {"agents": {
            "bridge_logger": {"status": "ok", "msg": "alive", "last_update": datetime.now(timezone.utc).isoformat()},
            "orchestrator": {"status": "ok", "msg": "running", "last_update": datetime.now(timezone.utc).isoformat()}
        }}
        METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        METRICS_PATH.write_text(json.dumps(dummy, ensure_ascii=False, indent=2))

    while True:
        # 1️⃣ Update our own heartbeat file
        update_heartbeat_file()
        if not heartbeat_is_fresh(interval):
            logger.warning("Monitor heartbeat check failed – continuing but flagging issue")

        metrics = read_metrics()
        agents = metrics.get("agents", {})
        for name, data in agents.items():
            # Check if agent reports an error status
            if data.get("status") == "error":
                logger.warning("Agent '%s' reported error: %s", name, data.get("msg"))
                if restart_tracker.record(name):
                    logger.critical("Fatal error: restart limit exceeded for %s – abandoning", name)
                    sys.exit(1)
                restart_agent(name)
                continue
            # Otherwise check heartbeat freshness
            if not check_agent_heartbeat(name, data, interval):
                logger.warning("Agent %s appears hung – attempting restart", name)
                if restart_tracker.record(name):
                    logger.critical("Fatal error: restart limit exceeded for %s – abandoning", name)
                    sys.exit(1)
                restart_agent(name)
        time.sleep(interval)

# ── ENTRYPOINT ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        monitor_loop()
    except Exception as e:
        logging.error(f"Critical failure: {e}")
        print(f"Critical failure: {e}")
        sys.exit(1)
