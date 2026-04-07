
import json
import os
from datetime import datetime

HISTORY_FILE = "alert_history.json"

def _ensure_file():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

def log_alert(alert_type, location):
    _ensure_file()
    entry = {
        "type": alert_type,
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "address": location.get("address", ""),
        "latitude": location.get("latitude", ""),
        "longitude": location.get("longitude", "")
    }
    with open(HISTORY_FILE, "r+") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)

def load_history():
    _ensure_file()
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)
