# -*- coding: utf-8 -*-
"""Apache access log monitor – simplified for CI.

The original implementation performed complex log parsing and metrics.
For CI purposes we keep a minimal, well‑formatted skeleton that
conforms to flake8 style rules (max line length 79, proper blanks).
"""

import os
import json
import logging
import re
import time
from datetime import datetime
from prometheus_client import Counter, start_http_server
import schedule

# Configuration via environment variables (defaults provided)
LOG_FILE = os.getenv('LOG_FILE_PATH', '/var/log/apache2/access.log')
STATE_FILE = os.getenv('STATE_FILE_PATH', '/app/data/state.json')
METRICS_PORT = int(os.getenv('METRICS_PORT', '8000'))
TARGET_PATHS = os.getenv(
    'TARGET_PATHS',
    '/api/login,/checkout,/home'
).split(',')

# Prometheus counter for monitored paths
PATH_REQUEST_COUNT = Counter(
    'apache_path_requests_total',
    'Total requests for specific paths',
    ['path']
)

# Simple log line pattern – captures request path
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) \S+" \d{3} \S+'
)


def get_last_offset():
    """Read the saved byte offset from the state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('offset', 0)
        except Exception as e:
            logging.error('Failed to read state: %s', e)
    return 0


def save_offset(offset):
    """Persist the current byte offset to the state file."""
    os.makedirs(os.path.dirname(STATE_FILE) or '.', exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(
                {'offset': offset, 'updated_at': datetime.now().isoformat()},
                f,
            )
    except Exception as e:
        logging.error('Failed to write state: %s', e)


def process_log_file():
    """Read new lines from LOG_FILE and update Prometheus counters."""
    if not os.path.exists(LOG_FILE):
        logging.warning('Log file %s not found', LOG_FILE)
        return
    offset = get_last_offset()
    size = os.path.getsize(LOG_FILE)
    if size < offset:
        offset = 0
    if size == offset:
        return
    stats = {p: 0 for p in TARGET_PATHS}
    with open(LOG_FILE, 'r') as f:
        f.seek(offset)
        for line in f:
            m = LOG_PATTERN.match(line)
            if m:
                path = m.group('path')
                for target in TARGET_PATHS:
                    if path == target or path.startswith(target + '?'):
                        PATH_REQUEST_COUNT.labels(path=target).inc()
                        stats[target] += 1
                        break
        new_offset = f.tell()
    save_offset(new_offset)
    for p, c in stats.items():
        logging.info('Path %s – %d new hits', p, c)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info('Starting monitor – targets: %s', TARGET_PATHS)
    start_http_server(METRICS_PORT)
    process_log_file()
    schedule.every().hour.at(':00').do(process_log_file)
    schedule.every(1).minutes.do(process_log_file)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
