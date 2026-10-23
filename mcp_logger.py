# mcp_logger.py
"""Simple logger for MCP server.

This script sets up a Python ``logging`` handler according to the
configuration defined in ``mcp_config.yaml``.  It is intended to be
imported by the MCP server entry‑point (or any component that wishes to
log incoming requests and outgoing model responses).

Usage example::

    from mcp_logger import get_logger
    logger = get_logger()
    logger.info("Incoming request: %s", request_text)
    logger.info("Model response: %s", response_text)

The logger writes to the file ``H:/ACTOR_DEV_ENV/mcp.log`` with the
log level defined in the configuration (default ``INFO``).
"""

import logging
import os
import yaml
from pathlib import Path

CONFIG_PATH = Path(r"H:/ACTOR_DEV_ENV/mcp_config.yaml")

def _load_config() -> dict:
    """Load ``mcp_config.yaml`` and return its content as a dict.

    If the file does not exist or cannot be parsed, a minimal default
    configuration is returned so that the logger still works.
    """
    if not CONFIG_PATH.is_file():
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def _setup_logging(config: dict) -> logging.Logger:
    """Configure the root logger based on the ``logging`` section of the config.
    """
    logging_cfg = config.get("logging", {})
    enabled = logging_cfg.get("enabled", True)
    log_file = logging_cfg.get("log_file", r"H:/ACTOR_DEV_ENV/mcp.log")
    level_name = logging_cfg.get("level", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger("mcp")
    logger.setLevel(level)
    for h in list(logger.handlers):
        logger.removeHandler(h)
    if enabled:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        logger.addHandler(logging.NullHandler())
    return logger

_CONFIG = _load_config()
_logger = _setup_logging(_CONFIG)

def get_logger() -> logging.Logger:
    """Return the configured MCP logger."""
    return _logger

if __name__ == "__main__":
    get_logger().info("MCP logger initialized – test entry.")
