from phase2.utils import read_json, write_json, utc_now

STATE_FILE = "phase2/data/portfolio_state.json"
POSITIONS_FILE = "phase2/data/positions.json"
NAV_FILE = "phase2/data/nav.json"

INITIAL_CAPITAL = 200000


def run():
    state = read_json(STATE_FILE, {})
    positions = read_json(POSITIONS_FILE, [])
    nav = read_json(NAV_FILE, {"value": INITIAL_CAPITAL})

    stocks = state.get("stocks", [])
    weights = state.get("weights", {})

    # If no signals → stay in cash
    if not stocks:
        write_json(POSITIONS_FILE, [])
        print("No signals → 100% cash")
        return

    capital = nav["value"]

    new_positions = []

    for s in stocks:
        w = weights.get(s, 0) / 100.0
        allocation = capital * w

        # qty will be computed later using live price engine
        new_positions.append({
            "symbol": s,
            "qty": 0,
            "avg_cost": 0,
            "allocated_capital": round(allocation, 2),
            "ts": utc_now(),
        })

    write_json(POSITIONS_FILE, new_positions)

    print("Capital deployed across", len(new_positions), "stocks")
