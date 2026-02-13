import json
import requests
from datetime import datetime

PORT = "phase2/data/portfolio_state.json"
RISK = "phase2/data/risk.json"
NAV = "phase2/data/nav.json"

EVENTS = "phase2/data/events.json"
COMMENT = "phase2/data/ai_commentary.json"

NEWS = "https://query1.finance.yahoo.com/v2/finance/news?symbols={}"
TOP = 3


def load(p):
    try:
        return json.load(open(p))
    except:
        return {}


def fetch(symbol):
    try:
        r = requests.get(NEWS.format(f"{symbol}.NS"), timeout=10).json()
        items = r.get("Content", {}).get("result", [])
        return [i.get("title") for i in items[:TOP] if i.get("title")]
    except:
        return []


def run():
    port = load(PORT)
    risk = load(RISK)
    nav = load(NAV)

    all_events = []
    for h in port.get("holdings", []):
        for e in fetch(h["symbol"]):
            all_events.append({"symbol": h["symbol"], "headline": e})

    events_payload = {"timestamp": datetime.utcnow().isoformat(), "count": len(all_events), "events": all_events}
    json.dump(events_payload, open(EVENTS, "w"), indent=2)

    text = (
        f"Portfolio NAV stands at ₹{nav.get('value',0):,.0f}, with return {nav.get('return_pct',0):.2f}%. "
        f"Current regime is {risk.get('regime','NA')} with 6-month CAGR {risk.get('cagr',0):.2f}% "
        f"and drawdown near {risk.get('max_dd',0):.2f}%. "
        f"{len(all_events)} material stock-specific events are under monitoring. "
        f"Positioning remains trend-aligned and risk-disciplined."
    )

    json.dump({"timestamp": datetime.utcnow().isoformat(), "commentary": text}, open(COMMENT, "w"), indent=2)

    print("Events:", len(all_events), "| Commentary ready")
