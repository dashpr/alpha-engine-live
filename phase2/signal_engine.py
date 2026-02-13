import pandas as pd
import numpy as np
import yfinance as yf
import json
from datetime import datetime

LOOKBACKS = [21, 63, 126]
VOL_WINDOW = 21
TOP_N = 20

UNIVERSE_FILE = "data/nifty200.csv"
OUTPUT_FILE = "phase2/data/signals.json"


def load_universe():
    df = pd.read_csv(UNIVERSE_FILE)
    return df["symbol"].dropna().tolist()


def fetch_prices(symbols):
    return yf.download(
        tickers=symbols,
        period="1y",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
        threads=True,
    )


def momentum_score(close):
    scores = [(close.pct_change(lb)) for lb in LOOKBACKS]
    return np.mean(scores, axis=0)


def volatility(close):
    return close.pct_change().rolling(VOL_WINDOW).std()


def build_signals():
    symbols = load_universe()
    prices = fetch_prices(symbols)

    records = []

    for s in symbols:
        try:
            close = prices[s]["Close"].dropna()
            if len(close) < 150:
                continue

            mom = momentum_score(close).iloc[-1]
            vol = volatility(close).iloc[-1]
            score = mom / (vol + 1e-9)

            records.append(
                {"symbol": s, "momentum": float(mom), "volatility": float(vol), "score": float(score)}
            )
        except Exception:
            continue

    df = pd.DataFrame(records).sort_values("score", ascending=False).head(TOP_N)

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "top_signals": df.to_dict(orient="records"),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("Signals generated:", len(df))
