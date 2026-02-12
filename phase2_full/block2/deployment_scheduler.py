import json
import pathlib
from datetime import datetime

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

STATE_FILE = OUTPUT / "deployment_state.json"
NAV_FILE = OUTPUT / "portfolio_nav.json"
SIGNAL_FILE = OUTPUT / "signal_state.json"
REBALANCE_FILE = OUTPUT / "rebalance_flag.json"

TOTAL_CAPITAL = 200000
MIN_WEEKS = 8
MAX_WEEKS = 12
STABILITY_DAYS = 5  # your 1-week stability rule

# --------------------------------------------------
# Load previous deployment state
# --------------------------------------------------
if STATE_FILE.exists():
    state = json.loads(STATE_FILE.read_text())
else:
    state = {
        "deployed": 0,
        "week": 0,
        "stable_days": 0,
        "start_date": datetime.utcnow().isoformat(),
    }

# --------------------------------------------------
# Read NAV + signal
# --------------------------------------------------
nav = json.loads(NAV_FILE.read_text())
signal = json.loads(SIGNAL_FILE.read_text())

current_value = nav["value"]
capital = nav["capital"]

drawdown = (current_value / capital - 1) * 100 if capital else 0
regime = signal["regime"]

# --------------------------------------------------
# Check signal stability (1-week gate)
# --------------------------------------------------
if REBALANCE_FILE.exists():
    rebalance_data = json.loads(REBALANCE_FILE.read_text())
    stable_today = not rebalance_data.get("rebalance_required", True)
else:
    stable_today = False

if stable_today:
    state["stable_days"] += 1
else:
    state["stable_days"] = 0

# --------------------------------------------------
# Do not deploy until stability achieved
# --------------------------------------------------
remaining = TOTAL_CAPITAL - state["deployed"]

if state["stable_days"] < STABILITY_DAYS or remaining <= 0:
    tranche = 0

else:
    base_tranche = TOTAL_CAPITAL / ((MIN_WEEKS + MAX_WEEKS) / 2)

    # Regime speed adjustment
    if regime == "RISK_ON":
        tranche = base_tranche * 1.2
    elif regime == "NEUTRAL":
        tranche = base_tranche * 0.7
    else:  # RISK_OFF
        tranche = 0

    # Your rule: dip-buy but reduced
    if drawdown <= -8:
        tranche *= 0.5

    tranche = max(0, min(tranche, remaining))

# --------------------------------------------------
# Update state
# --------------------------------------------------
state["deployed"] += tranche
state["week"] += 1
state["last_tranche"] = tranche
state["drawdown"] = drawdown
state["regime"] = regime

STATE_FILE.write_text(json.dumps(state, indent=2))

print("Deployment scheduler completed.")
