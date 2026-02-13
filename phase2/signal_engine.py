import pandas as pd
import numpy as np
import yfinance as yf
import json
from datetime import datetime

# ===============================
# CONFIG
# ===============================

LOOKBACKS = [21, 63, 126]  # 1M, 3M, 6M momentum
VOL_WINDOW = 21
TOP_N = 20

OUTPUT_PATH = "data/signals.json"


# ===============================
# LOAD NIFTY-200 UNIVERSE
# ===============================

def load_universe():
    df = pd.read_csv("data/nifty200.csv")
    return df["symbol"].dropna().unique().tolist()


# ===============================
# DOWNLOAD PRICE DATA
# ===============================

def fetch_prices(symbols):
    data = yf.download(
        tickers=symbols,
        period="1y",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    return data


# ===============================
# MOMENTUM CALCULATION
# ===============================

def compute_momentum(close):
    scores = []

    for lb in LOOKBACKS:
        scores.append(close.pct_change(lb))

    return np.mean(scores, axis=0)


# ===============================
# VOLATILITY FILTER
# ===============================

def compute_volatility(close):
    return close.pct_change().rolling(VOL_WINDOW).std()


# ===============================
# MAIN SIGNAL ENGINE
# ===============================

def build_signals():

    symbols = load_universe()
    price_data = fetch_prices(symbols)

    records = []

    for s in symbols:
        try:
            close = price_data[s]["Close"].dropna()

            if len(close) < 150:
                continue

            momentum = compute_momentum(close).iloc[-1]
            vol = compute_volatility(close).iloc[-1]

            score = momentum / (vol + 1e-6)

            records.append({
                "symbol": s,
                "momentum": float(momentum),
                "volatility": float(vol),
                "score": float(score)
            })

        except Exception:
            continue

    df = pd.DataFrame(records)

    if df.empty:
        return

    df = df.sort_values("score", ascending=False).head(TOP_N)

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "top_signals": df.to_dict(orient="records")
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)


# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    build_signals()
