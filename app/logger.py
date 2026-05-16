import os
import json
from datetime import datetime


LOG_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def _ensure_log_dir():
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join(LOG_BASE_DIR, date_str)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir, date_str


def log_report(data: dict, filename: str = None):
    log_dir, date_str = _ensure_log_dir()
    if filename is None:
        timestamp = datetime.now().strftime("%H-%M-%S")
        filename = f"report_{date_str}_{timestamp}.json"
    elif not filename.endswith(".json"):
        filename += ".json"
    filepath = os.path.join(log_dir, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return {
        "folder": log_dir,
        "filename": filename,
        "filepath": filepath,
        "method": "log_report",
        "description": "Writes a JSON report file to the date-based log directory",
    }
