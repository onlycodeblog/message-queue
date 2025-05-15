import os
import time
from pathlib import Path


def timestamped_log(msg: str, logfile: str):
    Path(os.path.dirname(logfile)).mkdir(parents=True, exist_ok=True)
    with open(logfile, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def ensure_log_dirs():
    Path("logs").mkdir(parents=True, exist_ok=True)
