import json
from pathlib import Path
from datetime import datetime

BASE = Path("phase2")
OUT = Path("phase2")

def load(name, default):
    p = BASE / name
    if p.exists():
        return json.loads(p.read_text())
    return default


nav = load("nav.json", {"capital": 200000, "value": 200000, "return_pct": 0})
positions = load("positions.json", [])
gov = load("governance.json", {"regime": "NEUTRAL"})
deploy = load("deployment.json", {"deployed": 0, "remaining": 200000})

# ---------- Phase-2C derived outputs ----------

holdings = [
    {"symbol": p["symbol"], "weight": p.get("weight", 0)}
    for p in positions
]

sectors = {}
for p in positions:
    sec = p.get("sector", "Unknown")
    sectors[sec] = sectors.get(sec, 0) + p.get("weight", 0)

sectors = [{"sector": k, "weight": v} for k, v in sectors.items()]

risk = {
    "cagr": 0,
    "max_dd": 0,
    "sharpe": 0,
}

events = [
    {
        "time": datetime.utcnow().isoformat(),
        "text": "System initialized. Awaiting market movement."
    }
]

ai = {
    "text": f"Portfolio value ₹{nav['value']:,}. Regime {gov['regime']}. Deployment ₹{deploy['deployed']:,}."
}

# ---------- write Phase-2C ----------
(OUT / "holdings.json").write_text(json.dumps(holdings, indent=2))
(OUT / "sectors.json").write_text(json.dumps(sectors, indent=2))
(OUT / "risk.json").write_text(json.dumps(risk, indent=2))
(OUT / "events.json").write_text(json.dumps(events, indent=2))
(OUT / "ai.json").write_text(json.dumps(ai, indent=2))

print("Phase-2C JSON generated.")
