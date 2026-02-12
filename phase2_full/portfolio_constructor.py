import json
import pathlib

OUTPUT = pathlib.Path("output")

signal_state = json.loads((OUTPUT / "signal_state.json").read_text())

regime = signal_state["regime"]
valid = signal_state["valid_signals"]

# --- Regime rules ---
if regime == "RISK_OFF" or len(valid) == 0:
    portfolio = {
        "stocks": [],
        "weights": {},
        "cash": 1.0,
        "regime": regime,
    }

else:
    # Max stock count by regime
    if regime == "RISK_ON":
        max_stocks = 10
    else:  # NEUTRAL
        max_stocks = 5

    selected = valid[:max_stocks]

    weight = round(1 / len(selected), 4)

    portfolio = {
        "stocks": selected,
        "weights": {s: weight for s in selected},
        "cash": 0.0,
        "regime": regime,
    }

(OUTPUT / "target_portfolio.json").write_text(json.dumps(portfolio, indent=2))

print("Portfolio constructor completed.")
