import json, pathlib


OUTPUT = pathlib.Path("output")


prices = json.loads((OUTPUT / "prices_live.json").read_text())
portfolio = json.loads((OUTPUT / "portfolio_live.json").read_text())


capital = 200000
value = 0


for s, w in portfolio["weights"].items():
price = prices[s]["price"] or 0
value += capital * w


nav = {
"capital": capital,
"value": value,
"return_pct": round((value/capital - 1) * 100, 2)
}


(OUTPUT / "portfolio_nav.json").write_text(json.dumps(nav, indent=2))
