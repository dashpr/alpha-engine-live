import json, pathlib, random


OUTPUT = pathlib.Path("output")


# Mock dynamic selection (replace with Model‑1 ranks later)
stocks = ["RELIANCE.NS", "INFY.NS"]


portfolio = {
"stocks": stocks,
"weights": {s: round(1/len(stocks), 2) for s in stocks}
}


(OUTPUT / "portfolio_live.json").write_text(json.dumps(portfolio, indent=2))
