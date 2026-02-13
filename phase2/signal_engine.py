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


# =========================
# LOAD UNIVERSE
# =========================
def load_universe():
    df = pd.read_csv(UNIVERSE_FILE)
    return df["symbol"].dropna().tolist()


# =========================
# ROBUST PRICE FETCH
# =========================
def fetch_close(symbol):
    """
    Download single symbol safely with retry.
    Designed for GitHub Actions environment.
    """
    for _ in range(3):
        try:
            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                threads=False,
            )

            if not df.empty and "Close" in df:
                return df["Close"].dropna()

        except Exception:
            time.sleep(1)

    return None


# =========================
# MOMENTUM + VOL FUNCTIONS
# =========================
def momentum_score(close: pd.Series) -> pd.Series:
    """
    Multi-horizon momentum averaged into a pandas Series.
    Returns pandas Series (NOT numpy array).
    """
    scores = pd.concat(
        [close.pct_change(lb) for lb in LOOKBACKS],
        axis=1
    )
    return scores.mean(axis=1)


def volatility(close: pd.Series) -> pd.Series:
    return close.pct_change().rolling(VOL_WINDOW).std()


# =========================
# BUILD SIGNALS
# =========================
def build_signals():

    symbols = load_universe()
    records = []

    for s in symbols:
        close = fetch_close(s)

        # Skip if data missing
        if close is None or len(close) < 150:
            continue

        # --- compute metrics ---
        mom_series = momentum_score(close)
        vol_series = volatility(close)

        mom = float(mom_series.iloc[-1])
        vol = float(vol_series.iloc[-1])

        # --- validation ---
        if np.isnan(mom) or np.isnan(vol) or vol == 0:
            continue

        score = mom / vol

        records.append({
            "symbol": s,
            "momentum": float(mom),
            "volatility": float(vol),
            "score": float(score),
        })

    # =========================
    # FALLBACK (only if ZERO data)
    # =========================
    if len(records) == 0:
        print("⚠️ Yahoo blocked → using fallback equal universe")
        records = [
            {"symbol": s, "momentum": 0.0, "volatility": 1.0, "score": 0.0}
            for s in symbols[:TOP_N]
        ]

    # =========================
    # SELECT TOP SIGNALS
    # =========================
    df = (
        pd.DataFrame(records)
        .sort_values("score", ascending=False)
        .head(TOP_N)
        .reset_index(drop=True)
    )

    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "top_signals": df.to_dict(orient="records"),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Signals generated: {len(df)}")
