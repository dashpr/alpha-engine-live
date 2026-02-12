import json
import pathlib

OUTPUT = pathlib.Path("output")

# Load required data safely
prices = json.loads((OUTPUT / "prices_live.json").read_text())
portfolio = json.loads((OUTPUT / "portfolio_live.json").read_text())

capital = 200000
value = 0

for s, w in portfolio["weights"].items():
    price = prices.get(s, {}).get("price")

    # If price missing → skip safely
    if price is None:
        continue

    value += capital * w

# Prevent divide-by-zero
if capital == 0:
    return_pct = 0
else:
    return_pct = round((value / capital - 1) * 100, 2)

nav = {
    "capital": capital,
    "value": round(value, 2),
    "return_pct": return_pct,
}

(OUTPUT / "portfolio_nav.json").write_text(json.dumps(nav, indent=2))

print("NAV simulation completed safely.")
