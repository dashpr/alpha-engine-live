import json
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# CONFIG
# =========================

SIGNAL_FILE = "data/signals.json"
PORTFOLIO_FILE = "phase2/data/portfolio_state.json"
POSITIONS_FILE = "phase2/data/positions.json"
SECTOR_FILE = "phase2/data/sectors.json"

N_STOCKS = 15
TOTAL_CAPITAL = 200000


# =========================
# LOAD SIGNALS
# =========================

def load_signals():
    with open(SIGNAL_FILE) as f:
        data = json.load(f)
    return pd.DataFrame(data["top_signals"])


# =========================
# RISK-BALANCED WEIGHTS
# =========================

def compute_weights(df: pd.DataFrame):
    """
    Inverse-volatility weighting for institutional stability.
    """

    inv_vol = 1 / (df["volatility"] + 1e-6)
    weights = inv_vol / inv_vol.sum()

    df["weight"] = weights
    return df


# =========================
# BUILD PORTFOLIO
# =========================

def build_portfolio():

    df = load_signals()

    if df.empty:
        print("No signals found.")
        return

    # Select top 15
    df = df.head(N_STOCKS).copy()

    # Compute weights
    df = compute_weights(df)

    # =========================
    # Portfolio State JSON
    # =========================
    portfolio_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "holdings": [
            {
                "symbol": row.symbol,
                "weight": round(row.weight * 100, 2)
            }
            for row in df.itertuples()
        ]
    }

    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio_state, f, indent=2)

    # =========================
    # Positions JSON (capital allocation)
    # =========================
    positions = []

    for row in df.itertuples():
        alloc = TOTAL_CAPITAL * row.weight

        positions.append({
            "symbol": row.symbol,
            "allocated_capital": round(alloc, 2),
            "qty": 0,          # filled later by MTM engine
            "avg_cost": 0
        })

    with open(POSITIONS_FILE, "w") as f:
        json.dump({"positions": positions}, f, indent=2)

    # =========================
    # Sector Placeholder (real mapping later)
    # =========================
    sector_alloc = (
        df.groupby(lambda x: "UNKNOWN")["weight"]
        .sum()
        .reset_index()
    )

    sectors = [
        {
            "sector": "UNKNOWN",
            "weight": 100.0
        }
    ]

    with open(SECTOR_FILE, "w") as f:
        json.dump(sectors, f, indent=2)

    print("Portfolio constructed with", len(df), "stocks.")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    build_portfolio()
