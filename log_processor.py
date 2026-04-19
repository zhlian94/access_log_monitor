import time
import os
import re
import json
import logging
from datetime import datetime
import schedule
from prometheus_client import start_http_server, Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Environment configuration
LOG_FILE = os.getenv('LOG_FILE_PATH', '/var/log/apache2/access.log')
STATE_FILE = os.getenv('STATE_FILE_PATH', '/app/data/state.json')
METRICS_PORT = int(os.getenv('METRICS_PORT', '8000'))
# Paths to monitor (comma separated), default to a few sample ones
TARGET_PATHS_STR = os.getenv('TARGET_PATHS', '/api/login,/checkout,/home,/api/data')
TARGET_PATHS = [p.strip() for p in TARGET_PATHS_STR.split(',')]

# Define Prometheus metrics
# Using labels to track counts per path
PATH_REQUEST_COUNT = Counter(
    'apache_path_requests_total',
    'Total requests for specific paths',
    ['path']
)

# Regex to parse standard Apache combined/common log log format
# Example: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /api/login HTTP/1.0" 200 2326
LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<proto>\S+)" (?P<status>\d{3}) (?P<bytes>\S+)'
)

def get_last_offset():
    """Retrieve the last read byte offset from the state file."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                return state.get('offset', 0)
        except Exception as e:
            logging.error(f"Error reading state file {STATE_FILE}: {e}")
            return 0
    return 0

def save_offset(offset):
    """Save the current byte offset to the state file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(STATE_FILE) or '.', exist_ok=True)
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump({'offset': offset, 'updated_at': datetime.now().isoformat()}, f)
    except Exception as e:
        logging.error(f"Error writing state file {STATE_FILE}: {e}")

def process_log_file():
    """Process the Apache access log from the last known offset."""
    if not os.path.exists(LOG_FILE):
        logging.warning(f"Log file {LOG_FILE} not found. Waiting for it to appear.")
        return

    offset = get_last_offset()
    current_size = os.path.getsize(LOG_FILE)

    if current_size < offset:
        # File was likely rotated, reset offset
        logging.info("Log file size is smaller than offset. File might have been rotated. Resetting offset.")
        offset = 0

    if current_size == offset:
        logging.info("No new log entries to process.")
        return

    logging.info(f"Processing {LOG_FILE} starting from offset {offset}")

    stats_this_run = {path: 0 for path in TARGET_PATHS}

    with open(LOG_FILE, 'r') as f:
        f.seek(offset)
        for line in f:
            match = LOG_PATTERN.match(line)
            if match:
                path = match.group('path')
                
                # Check if the path requested exactly matches or starts with our target paths
                for target in TARGET_PATHS:
                    if path == target or path.startswith(target + "?"):
                        PATH_REQUEST_COUNT.labels(path=target).inc()
                        stats_this_run[target] += 1
                        break

        # Save new offset
        new_offset = f.tell()
        save_offset(new_offset)

    # Print stats to terminal for demo purposes
    logging.info("--- Hourly/Run Processing Stats ---")
    for path, count in stats_this_run.items():
        logging.info(f"Path: {path} | New Hits in this run: {count}")
    logging.info("-----------------------------------")


def main():
    logging.info(f"Starting Apache Access Log Monitor.")
    logging.info(f"Monitoring paths: {TARGET_PATHS}")
    logging.info(f"Exposing Prometheus metrics on port {METRICS_PORT}")
    
    # Start the Prometheus HTTP server
    start_http_server(METRICS_PORT)

    # Do an initial run on startup
    process_log_file()

    # The user requested processing every hour and every day.
    # We will schedule the process_log_file job to run every hour. 
    # (Since it runs every hour, it naturally covers the "every day" requirement, 
    # but strictly we can visualize this grouped per hour/day in Grafana).
    schedule.every().hour.at(":00").do(process_log_file)
    
    # For demo purposes, we will ALSO run it every 1 minute so the user doesn't have to wait an hour.
    schedule.every(1).minutes.do(process_log_file)

    logging.info("Scheduler started. Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
