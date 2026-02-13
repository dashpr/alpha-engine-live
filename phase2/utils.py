import json
from pathlib import Path
from datetime import datetime, timezone


DATA_DIR = Path("phase2/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text())


def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def utc_now():
    return datetime.now(timezone.utc).isoformat()
