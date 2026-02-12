import json
import pathlib

OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)

prices = json.loads((OUTPUT / "prices_live.json").read_text())
portfolio = json.loads((OUTPUT / "portfolio_live.json").read_text())

POSITIONS_FILE = OUTPUT / "portfolio_positions.json"

capital = 200000


# --------------------------------------------------
# STEP 1 — Create positions only once (persistent)
# --------------------------------------------------
if not POSITIONS_FILE.exists():

    positions = {}

    for s, w in portfolio["weights"].items():
        price = prices.get(s, {}).get("price")

        if price is None or price == 0:
            continue

        allocation = capital * w
        quantity = allocation / price

        positions[s] = {
            "entry_price": price,
            "quantity": quantity,
            "allocation": allocation,
        }

    POSITIONS_FILE.write_text(json.dumps(positions, indent=2))


# --------------------------------------------------
# STEP 2 — Load persistent positions
# --------------------------------------------------
positions = json.loads(POSITIONS_FILE.read_text())


# --------------------------------------------------
# STEP 3 — Mark-to-market valuation
# --------------------------------------------------
value = 0

for s, pos in positions.items():
    current_price = prices.get(s, {}).get("price")

    if current_price is None:
        continue

    value += pos["quantity"] * current_price


# --------------------------------------------------
# STEP 4 — Compute NAV safely
# --------------------------------------------------
return_pct = round((value / capital - 1) * 100, 2) if capital else 0

nav = {
    "capital": capital,
    "value": round(value, 2),
    "return_pct": return_pct,
}

(OUTPUT / "portfolio_nav.json").write_text(json.dumps(nav, indent=2))

print("NAV with persistent positions computed.")
