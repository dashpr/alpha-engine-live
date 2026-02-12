import requests
import json
import pathlib
import time

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

SYMBOLS = ["RELIANCE.NS", "INFY.NS"]

prices = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

for s in SYMBOLS:
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={s}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        # If response empty or blocked → skip safely
        if r.status_code != 200 or not r.text.strip():
            raise ValueError("Empty or blocked response")

        data = r.json()
        result = data.get("quoteResponse", {}).get("result", [])

        if not result:
            raise ValueError("No quote data")

        q = result[0]

        prices[s] = {
            "price": q.get("regularMarketPrice"),
            "change_pct": q.get("regularMarketChangePercent"),
        }

        time.sleep(1)  # avoid rate-limit

    except Exception as e:
        # Never crash pipeline — store None safely
        prices[s] = {
            "price": None,
            "change_pct": None,
            "error": str(e)
        }

# Always write output (even if API failed)
(OUTPUT / "prices_live.json").write_text(json.dumps(prices, indent=2))

print("Live prices update completed safely.")
