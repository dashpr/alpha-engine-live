import json
import pathlib

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

# --- MOCK MODEL‑1 INPUT (replace later with real model output) ---
universe_scores = {
    "RELIANCE.NS": 0.72,
    "INFY.NS": 0.55,
    "HDFCBANK.NS": 0.63,
    "TCS.NS": 0.48,
}

# --- HYBRID RULE (C) ---
ABSOLUTE_CUTOFF = 0.60
TOP_PERCENTILE = 0.5  # top 50% by score

# Rank stocks
ranked = sorted(universe_scores.items(), key=lambda x: x[1], reverse=True)

# Determine percentile cutoff index
cut_index = max(1, int(len(ranked) * TOP_PERCENTILE))

# Stocks that are BOTH top‑ranked AND above absolute cutoff
valid_signals = [
    s for s, score in ranked[:cut_index] if score >= ABSOLUTE_CUTOFF
]

# Determine regime
if len(valid_signals) == 0:
    regime = "RISK_OFF"
elif len(valid_signals) <= 2:
    regime = "NEUTRAL"
else:
    regime = "RISK_ON"

signal_state = {
    "regime": regime,
    "valid_signals": valid_signals,
    "scores": universe_scores,
}

(OUTPUT / "signal_state.json").write_text(json.dumps(signal_state, indent=2))

print("Signal interpreter completed.")
