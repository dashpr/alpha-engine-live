import json
import pathlib
from datetime import datetime

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

# --- Placeholder structured events ---
events = {
    "timestamp": datetime.utcnow().isoformat(),
    "highlights": [
        "No abnormal sector risk detected.",
        "Macro environment stable for staged deployment.",
        "Monitoring earnings and global liquidity signals."
    ]
}

(OUTPUT / "event_feed.json").write_text(json.dumps(events, indent=2))

print("Event feed generated.")
