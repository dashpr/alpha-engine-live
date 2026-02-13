from phase2.utils import read_json, write_json, utc_now

STATE_FILE = "phase2/data/portfolio_state.json"
WATCH_FILE = "phase2/data/watchlist_history.json"


def run():
    state = read_json(STATE_FILE, {})
    history = read_json(WATCH_FILE, [])

    current = set(state.get("stocks", []))
    previous = {h["symbol"] for h in history if h.get("exit_ts") is None}

    # New entries
    for sym in current - previous:
        history.append({
            "symbol": sym,
            "entry_ts": utc_now(),
            "exit_ts": None,
            "reason": "New signal inclusion",
        })

    # Exits
    for rec in history:
        if rec["symbol"] not in current and rec["exit_ts"] is None:
            rec["exit_ts"] = utc_now()
            rec["reason"] = "Signal removal"

    write_json(WATCH_FILE, history)

    print("Watchlist memory updated")
