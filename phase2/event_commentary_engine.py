import json
from datetime import datetime
import requests

# =========================
# FILE PATHS
# =========================

PORTFOLIO_FILE = "phase2/data/portfolio_state.json"
RISK_FILE = "phase2/data/risk.json"
NAV_FILE = "phase2/data/nav.json"

EVENTS_FILE = "phase2/data/events.json"
COMMENTARY_FILE = "phase2/data/ai_commentary.json"


# =========================
# CONFIG
# =========================

TOP_EVENTS_PER_STOCK = 3
YAHOO_NEWS_URL = "https://query1.finance.yahoo.com/v2/finance/news?symbols={}"


# =========================
# LOAD HELPERS
# =========================

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


# =========================
# FETCH EVENTS FROM YAHOO
# =========================

def fetch_events(symbol: str):
    """
    Fetch top material Yahoo Finance news for a stock.
    Returns list of headlines.
    """
    try:
        url = YAHOO_NEWS_URL.format(f"{symbol}.NS")
        r = requests.get(url, timeout=10)
        data = r.json()

        news_items = data.get("Content", {}).get("result", [])

        headlines = []
        for item in news_items[:TOP_EVENTS_PER_STOCK]:
            title = item.get("title")
            if title:
                headlines.append(title)

        return headlines

    except Exception:
        return []


# =========================
# BUILD EVENTS.JSON
# =========================

def build_events(portfolio):

    all_events = []

    for h in portfolio.get("holdings", []):
        symbol = h["symbol"]
        headlines = fetch_events(symbol)

        for head in headlines:
            all_events.append({
                "symbol": symbol,
                "headline": head
            })

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "count": len(all_events),
        "events": all_events
    }

    with open(EVENTS_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    return payload


# =========================
# BUILD CIO COMMENTARY
# =========================

def build_commentary(nav, risk, portfolio, events):

    value = nav.get("value", 0)
    ret = nav.get("return_pct", 0)

    regime = risk.get("regime", "UNKNOWN")
    cagr = risk.get("cagr", 0)
    dd = risk.get("max_dd", 0)

    holdings = portfolio.get("holdings", [])
    top_symbols = ", ".join([h["symbol"] for h in holdings[:3]])

    event_count = events.get("count", 0)

    # Institutional CIO snapshot paragraph
    text = (
        f"Portfolio NAV stands at ₹{value:,.0f}, reflecting a return of {ret:.2f}% "
        f"since inception. The current risk regime is assessed as {regime}, with "
        f"a rolling 6-month CAGR of {cagr:.2f}% and maximum drawdown contained near "
        f"{dd:.2f}%. Portfolio positioning remains concentrated in leading momentum "
        f"names such as {top_symbols}, aligned with prevailing trend strength across "
        f"the NIFTY-200 universe. Recent intelligence captured {event_count} material "
        f"stock-specific developments, which continue to be monitored for potential "
        f"impact on allocation and risk posture. Overall stance remains disciplined, "
        f"trend-aligned, and responsive to evolving market conditions."
    )

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "commentary": text
    }

    with open(COMMENTARY_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    return payload


# =========================
# MAIN ENGINE
# =========================

def run():

    portfolio = load_json(PORTFOLIO_FILE, {})
    risk = load_json(RISK_FILE, {})
    nav = load_json(NAV_FILE, {})

    # 1) Events
    events = build_events(portfolio)

    # 2) Commentary
    commentary = build_commentary(nav, risk, portfolio, events)

    print("Event & Commentary engine updated.")
    print("Events:", events.get("count", 0))
    print("CIO commentary generated.")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    run()
