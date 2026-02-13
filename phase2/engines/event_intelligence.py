import requests
from datetime import datetime, timezone
from phase2.utils import read_json, write_json, utc_now

PORTFOLIO_FILE = "phase2/data/portfolio_state.json"
EVENT_FILE = "phase2/data/events.json"


NEWS_API = "https://query1.finance.yahoo.com/v2/finance/news?symbols={symbol}"


def fetch_events(symbol: str):
    """Fetch material news for a single NSE stock via Yahoo endpoint."""
    try:
        url = NEWS_API.format(symbol=f"{symbol}.NS")
        r = requests.get(url, timeout=10)
        data = r.json().get("Content", {}).get("result", [])
    except Exception:
        return []

    events = []

    for item in data[:3]:  # limit to top material headlines
        title = item.get("title")
        pub = item.get("pubDate")

        if not title:
            continue

        events.append({
            "symbol": symbol,
            "headline": title,
            "published": pub,
        })

    return events


def run():
    state = read_json(PORTFOLIO_FILE, {})
    stocks = state.get("stocks", [])

    all_events = []

    for s in stocks:
        all_events.extend(fetch_events(s))

    payload = {
        "timestamp": utc_now(),
        "count": len(all_events),
        "events": all_events,
    }

    write_json(EVENT_FILE, payload)

    print("Event intelligence updated:", len(all_events), "items")
