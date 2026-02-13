import json
import pathlib
from datetime import datetime

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

signal = json.loads((OUTPUT / "signal_state.json").read_text())
nav = json.loads((OUTPUT / "portfolio_nav.json").read_text())
deploy = json.loads((OUTPUT / "deployment_state.json").read_text())

regime = signal["regime"]
return_pct = nav["return_pct"]
deployed = deploy["deployed"]

# --- Model‑driven reasoning ---
if regime == "RISK_OFF":
    stance = "Portfolio remains defensive with high cash allocation due to weak absolute signals."
elif regime == "NEUTRAL":
    stance = "Selective exposure maintained while awaiting stronger confirmation from Model‑1 signals."
else:
    stance = "Risk‑on posture supported by multiple stocks passing absolute momentum thresholds."

if return_pct < -5:
    performance_note = "Short‑term drawdown observed; deployment pace automatically reduced per capital‑protection rule."
elif return_pct > 5:
    performance_note = "Positive performance supporting continued staged deployment."
else:
    performance_note = "Portfolio performance remains within normal fluctuation range during deployment phase."

summary = f"""
Date: {datetime.utcnow().date()}

Regime: {regime}
Capital Deployed: ₹{deployed:,.0f}
Return: {return_pct:.2f}%

{stance}
{performance_note}
""".strip()

(OUTPUT / "ai_brief.txt").write_text(summary)

print("AI decision brain updated.")
