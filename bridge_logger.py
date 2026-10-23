import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

METRICS_PATH = Path('H:/ACTOR_DEV_ENV/mcp_metrics.json')
LOG_FILE = Path('H:/ACTOR_DEV_ENV/bridge_logger.log')
HEARTBEAT_INTERVAL = 10  # seconds, updated per request

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def update_heartbeat():
    now = datetime.now(timezone.utc).isoformat()
    try:
        metrics = json.loads(METRICS_PATH.read_text())
    except Exception:
        metrics = {}
    prev = metrics.get('bridge_logger', {})
    last = prev.get('last_update')
    if last:
        try:
            last_dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - last_dt).total_seconds()
            stable = age <= HEARTBEAT_INTERVAL * 2
            logging.info('Previous heartbeat age %.1f sec, stability: %s', age, stable)
        except Exception:
            logging.warning('Failed to parse previous timestamp')
    else:
        logging.info('No previous heartbeat recorded')
    metrics['bridge_logger'] = {'last_update': now}
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2))
    logging.info('Heartbeat sent at %s', now)

def main():
    logging.info('Bridge logger started')
    while True:
        update_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == '__main__':
    main()
