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
# SAFE CLOSE FETCH
# =========================
def fetch_close(symbol):
    """
    Robust Yahoo download with retry.
    Always returns a clean pandas Series or None.
    """
    for _ in range(3):
        try:
            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                threads=False,
                auto_adjust=True,
            )

            if df is None or df.empty:
                time.sleep(1)
                continue

            # Handle possible multi-index columns
            if isinstance(df.columns, pd.MultiIndex):
                if ("Close" in df.columns.get_level_values(0)):
                    close = df["Close"]
                else:
                    close = df.iloc[:, 0]
            else:
                close = df["Close"] if "Close" in df else df.iloc[:, 0]

            close = close.dropna()

            if len(close) > 0:
                return close

        except Exception:
            time.sleep(1)

    return None


# =========================
# MOMENTUM + VOL
# =========================
def momentum_score(close: pd.Series) -> float:
    """Return scalar multi-horizon momentum."""
    vals = []
    for lb in LOOKBACKS:
        if len(close) > lb:
            vals.append(close.pct_change(lb).iloc[-1])
    return float(np.nanmean(vals)) if len(vals) > 0 else np.nan


def volatility(close: pd.Series) -> float:
    """Return scalar rolling volatility."""
    if len(close) < VOL_WINDOW:
        return np.nan
    return float(close.pct_change().rolling(VOL_WINDOW).std().iloc[-1])


# =========================
# BUILD SIGNALS
# =========================
def build_signals():

    symbols = load_universe()
    records = []

    for s in symbols:
        close = fetch_close(s)

        if close is None or len(close) < 150:
            continue

        mom = momentum_score(close)
        vol = volatility(close)

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
    # FALLBACK ONLY IF ZERO DATA
    # =========================
    if len(records) == 0:
        print("⚠️ Yahoo blocked → fallback equal universe")
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
