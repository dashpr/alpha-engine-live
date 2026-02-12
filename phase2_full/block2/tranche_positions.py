import json
import pathlib

OUTPUT = pathlib.Path("output")

PRICES = json.loads((OUTPUT / "prices_live.json").read_text())
PORTFOLIO = json.loads((OUTPUT / "target_portfolio.json").read_text())
DEPLOY = json.loads((OUTPUT / "deployment_state.json").read_text())

POSITIONS_FILE = OUTPUT / "portfolio_positions.json"

positions = json.loads(POSITIONS_FILE.read_text()) if POSITIONS_FILE.exists() else {}

tranche = DEPLOY.get("last_tranche", 0)

if tranche <= 0 or not PORTFOLIO["stocks"]:
    POSITIONS_FILE.write_text(json.dumps(positions, indent=2))
    print("No tranche deployed.")
    raise SystemExit

per_stock = tranche / len(PORTFOLIO["stocks"])

for s in PORTFOLIO["stocks"]:
    price = PRICES.get(s, {}).get("price")
    if not price:
        continue

    qty = per_stock / price

    if s not in positions:
        positions[s] = {"quantity": 0, "total_cost": 0}

    positions[s]["quantity"] += qty
    positions[s]["total_cost"] += per_stock

POSITIONS_FILE.write_text(json.dumps(positions, indent=2))

print("Tranche positions updated.")
