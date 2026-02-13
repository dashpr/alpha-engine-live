import pandas as pd
import numpy as np
import yfinance as yf
import json
import time
from datetime import datetime

LOOKBACKS = [21, 63, 126]
VOL_WINDOW = 21
TOP_N = 20

UNIVERSE_FILE = "data/nifty200.csv"
OUTPUT_FILE = "phase2/data/signals.json"


def load_universe():
    df = pd.read_csv(UNIVERSE_FILE)
    return df["symbol"].dropna().tolist()


def fetch_close(symbol):
    """Robust single-symbol fetch with retry."""
    for _ in range(3):
        try:
            df = yf.download(symbol, period="1y", interval="1d", progress=False)
            if not df.empty:
                return df["Close"].dropna()
        except Exception:
            time.sleep(1)
    return None


def momentum_score(close):
    scores = [close.pct_change(lb) for lb in LOOKBACKS]
    return np.mean(scores, axis=0)


def volatility(close):
    return close.pct_change().rolling(VOL_WINDOW).std()


def build_signals():

    symbols = load_universe()
    records = []

    for s in symbols:
        close = fetch_close(s)

        if close is None or len(close) < 150:
            continue

        mom = momentum_score(close).iloc[-1]
        vol = volatility(close).iloc[-1]

        if pd.isna(mom) or pd.isna(vol) or vol == 0:
            continue

        score = mom / vol

        records.append(
            {"symbol": s, "momentum": float(mom), "volatility": float(vol), "score": float(score)}
        )

    # ---------- fallback only if ZERO data ----------
    if len(records) == 0:
        print("⚠️ Yahoo blocked → fallback equal universe")
        records = [{"symbol": s, "momentum": 0, "volatility": 1, "score": 0} for s in symbols[:TOP_N]]

    df = pd.DataFrame(records).sort_values("score", ascending=False).head(TOP_N)

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "top_signals": df.to_dict(orient="records"),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print("✅ Signals generated:", len(df))
