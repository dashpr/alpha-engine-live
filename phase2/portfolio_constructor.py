import json
import pandas as pd
from datetime import datetime

SIGNAL_FILE = "phase2/data/signals.json"
PORTFOLIO_FILE = "phase2/data/portfolio_state.json"
POSITIONS_FILE = "phase2/data/positions.json"
SECTOR_FILE = "phase2/data/sectors.json"

N_STOCKS = 15
TOTAL_CAPITAL = 200000


def load_signals():
    with open(SIGNAL_FILE) as f:
        return pd.DataFrame(json.load(f)["top_signals"])


def inverse_vol_weights(df):
    inv = 1 / (df["volatility"] + 1e-9)
    w = inv / inv.sum()
    df["weight"] = w
    return df


def build_portfolio():
    df = load_signals().head(N_STOCKS)
    df = inverse_vol_weights(df)

    portfolio = {
        "timestamp": datetime.utcnow().isoformat(),
        "holdings": [{"symbol": r.symbol, "weight": round(r.weight * 100, 2)} for r in df.itertuples()],
    }

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=2)

    positions = []
    for r in df.itertuples():
        alloc = TOTAL_CAPITAL * r.weight
        positions.append(
            {"symbol": r.symbol, "allocated_capital": round(alloc, 2), "qty": 0, "avg_cost": 0}
        )

    with open(POSITIONS_FILE, "w") as f:
        json.dump({"positions": positions}, f, indent=2)

    with open(SECTOR_FILE, "w") as f:
        json.dump([{"sector": "DYNAMIC", "weight": 100}], f, indent=2)

    print("Portfolio built:", len(df), "stocks")
