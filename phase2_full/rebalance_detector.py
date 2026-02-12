import json
import pathlib

OUTPUT = pathlib.Path("output")
FLAG_FILE = OUTPUT / "rebalance_flag.json"

current = json.loads((OUTPUT / "signal_state.json").read_text())

# Load previous state if exists
if FLAG_FILE.exists():
    previous = json.loads(FLAG_FILE.read_text()).get("last_signal_state")
else:
    previous = None

# Determine rebalance need
rebalance = previous != current

FLAG_FILE.write_text(
    json.dumps(
        {
            "rebalance_required": rebalance,
            "last_signal_state": current,
        },
        indent=2,
    )
)

print("Rebalance detector completed.")
