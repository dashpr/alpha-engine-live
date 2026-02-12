import requests
import json
import pathlib
import time

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

SYMBOLS = ["RELIANCE.NS", "INFY.NS"]

# Demo fallback prices (used only if API blocked)
FALLBACK = {
    "RELIANCE.NS": 2900,
    "INFY.NS": 1600,
}

prices = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

for s in SYMBOLS:
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={s}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        if r.status_code != 200 or not r.text.strip():
            raise ValueError("Blocked")

        data = r.json()
        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            raise ValueError("No data")

        q = result[0]
        price = q.get("regularMarketPrice")

        if price is None:
            raise ValueError("Null price")

        prices[s] = {
            "price": price,
            "change_pct": q.get("regularMarketChangePercent"),
            "source": "live"
        }

        time.sleep(1)

    except Exception:
        # Use fallback so system stays alive
        prices[s] = {
            "price": FALLBACK[s],
            "change_pct": 0,
            "source": "fallback"
        }

(OUTPUT / "prices_live.json").write_text(json.dumps(prices, indent=2))

print("Prices updated with fallback protection.")
