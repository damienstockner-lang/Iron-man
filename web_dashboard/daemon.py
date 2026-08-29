#!/usr/bin/env python3
import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "friday_daemon.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("friday_daemon")

DASHBOARD_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
PYTHON = sys.executable


def start_dashboard():
    cmd = [PYTHON, DASHBOARD_SCRIPT]
    logger.info("Starting Friday Dashboard: %s", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(DASHBOARD_SCRIPT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    logger.info("Dashboard PID: %d", proc.pid)
    return proc


def tail_output(proc):
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            logger.info("[dashboard] %s", line)


def run_forever():
    logger.info("Friday Daemon started at %s", datetime.now().isoformat())
    while True:
        proc = start_dashboard()
        try:
            tail_output(proc)
        except Exception as exc:
            logger.error("Dashboard stream error: %s", exc)
        ret = proc.poll()
        logger.warning("Dashboard exited with code %s. Restarting in 3s...", ret)
        time.sleep(3)


def handle_signal(signum, frame):
    logger.info("Received signal %s, shutting down daemon.", signum)
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    run_forever()


if __name__ == "__main__":
    main()
