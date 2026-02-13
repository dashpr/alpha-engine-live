from phase2.utils import read_json, write_json, utc_now

MODEL_FILE = "output/target_portfolio.json"
STATE_FILE = "phase2/data/portfolio_state.json"


def run():
    model = read_json(MODEL_FILE, {})

    stocks = model.get("stocks", [])
    weights = model.get("weights", {})
    regime = model.get("regime", "NEUTRAL")
    rebalance = model.get("rebalance_required", False)

    state = {
        "timestamp": utc_now(),
        "stocks": stocks,
        "weights": weights,
        "regime": regime,
        "rebalance_required": rebalance,
    }

    write_json(STATE_FILE, state)

    print("Portfolio state updated:", len(stocks), "stocks")
