import json

# -------------------------------
# Read NAV + signal
# -------------------------------
nav = json.loads(NAV_FILE.read_text())
signal = json.loads(SIGNAL_FILE.read_text())

current_value = nav["value"]
capital = nav["capital"]

# Drawdown % from capital
if capital > 0:
    drawdown = (current_value / capital - 1) * 100
else:
    drawdown = 0

regime = signal["regime"]

# -------------------------------
# Decide weekly tranche
# -------------------------------
remaining = TOTAL_CAPITAL - state["deployed"]

if remaining <= 0:
    tranche = 0

else:
    base_tranche = TOTAL_CAPITAL / ((MIN_WEEKS + MAX_WEEKS) / 2)

    # Regime acceleration / slowdown
    if regime == "RISK_ON":
        tranche = base_tranche * 1.2
    elif regime == "NEUTRAL":
        tranche = base_tranche * 0.7
    else:  # RISK_OFF
        tranche = 0

    # -------------------------------
    # YOUR RULE: Dip buying but reduced
    # -------------------------------
    if drawdown <= -8:
        tranche *= 0.5  # reduced deployment in drawdown

    tranche = max(0, min(tranche, remaining))

# -------------------------------
# Update state
# -------------------------------
state["deployed"] += tranche
state["week"] += 1
state["last_tranche"] = tranche
state["drawdown"] = drawdown
state["regime"] = regime

STATE_FILE.write_text(json.dumps(state, indent=2))

print("Deployment scheduler completed.")
