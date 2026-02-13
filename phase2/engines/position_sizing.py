from phase2.utils import read_json, write_json, utc_now

POSITIONS_FILE = "phase2/data/positions.json"
PRICES_FILE = "phase2/data/live_prices.json"

ROTATION_RATE = 0.25  # 25% rotation per cycle (institutional gradual shift)


def run():
    positions = read_json(POSITIONS_FILE, [])
    prices = read_json(PRICES_FILE, {})

    new_positions = []

    for p in positions:
        sym = f"{p['symbol']}.NS"
        alloc = p.get("allocated_capital", 0)

        price = prices.get(sym, {}).get("price", 0)

        if price <= 0:
            new_positions.append(p)
            continue

        target_qty = alloc / price

        # LOCK-B gradual rotation
        current_qty = p.get("qty", 0)
        qty = current_qty + (target_qty - current_qty) * ROTATION_RATE

        new_positions.append({
            "symbol": p["symbol"],
            "qty": round(qty, 4),
            "avg_cost": round(price, 2) if qty > 0 else 0,
            "allocated_capital": alloc,
            "ts": utc_now(),
        })

    write_json(POSITIONS_FILE, new_positions)

    print("Position sizing updated")
