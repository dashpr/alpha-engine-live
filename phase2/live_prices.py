import requests, json, pathlib


OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)


SYMBOLS = ["RELIANCE.NS", "INFY.NS"]


prices = {}


for s in SYMBOLS:
url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={s}"
r = requests.get(url, timeout=10).json()
q = r["quoteResponse"]["result"][0]


prices[s] = {
"price": q.get("regularMarketPrice"),
"change_pct": q.get("regularMarketChangePercent"),
}


(OUTPUT / "prices_live.json").write_text(json.dumps(prices, indent=2))
