from phase2.utils import read_json, write_json

POSITIONS_FILE = "phase2/data/positions.json"
PRICES_FILE = "phase2/data/live_prices.json"
NAV_FILE = "phase2/data/nav.json"

INITIAL_CAPITAL = 200000


def run():
    positions = read_json(POSITIONS_FILE, [])
    prices = read_json(PRICES_FILE, {})

    invested_value = 0

    for p in positions:
        sym = f"{p['symbol']}.NS"
        qty = p.get("qty", 0)
        price = prices.get(sym, {}).get("price", 0)

        invested_value += qty * price

    value = INITIAL_CAPITAL - sum(p["allocated_capital"] for p in positions) + invested_value

    nav = {
        "capital": INITIAL_CAPITAL,
        "value": round(value, 2),
        "return_pct": round((value - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100, 2),
    }

    write_json(NAV_FILE, nav)

    print("NAV recalculated:", nav["value"])
