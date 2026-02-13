import requests
from phase2.utils import write_json, read_json, utc_now

PORTFOLIO_FILE = "output/target_portfolio.json"
LIVE_PRICES_FILE = "phase2/data/live_prices.json"


YAHOO_URL = (
    "https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbols}"
)


def fetch_prices(symbols):
    if not symbols:
        return {}

    url = YAHOO_URL.format(symbols=",".join(symbols))

    try:
        r = requests.get(url, timeout=10)
        data = r.json()["quoteResponse"]["result"]
    except Exception:
        return {}

    prices = {}

    for row in data:
        sym = row.get("symbol")
        price = row.get("regularMarketPrice")
        change = row.get("regularMarketChangePercent")

        if sym and price is not None:
            prices[sym] = {
                "price": float(price),
                "change_pct": float(change or 0),
                "ts": utc_now(),
            }

    return prices


def run():
    model = read_json(PORTFOLIO_FILE, {})

    stocks = model.get("stocks", [])

    # Convert to NSE Yahoo symbols
    symbols = [f"{s}.NS" for s in stocks]

    prices = fetch_prices(symbols)

    write_json(LIVE_PRICES_FILE, prices)

    print("Market data updated:", len(prices), "symbols")
