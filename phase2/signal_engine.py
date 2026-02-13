"""
PHASE-2 INSTITUTIONAL SIGNAL ENGINE (FINAL CI-STABLE)
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf

# ================= CONFIG =================

DATA_PATH = "data"
UNIVERSE_FILE = os.path.join(DATA_PATH, "nifty200.csv")

LOOKBACK_DAYS = 252
MOM_WINDOWS = [21, 63, 126]
VOL_WINDOW = 63

MIN_PRICE_HISTORY = 150
TOP_N_SIGNALS = 30


# ================= LOGGING =================

def log(msg: str):
    print(f"[SIGNAL_ENGINE] {msg}")


def safe_float(value) -> float:
    try:
        if hasattr(value, "item"):
            return float(value.item())
        return float(value)
    except Exception:
        return 0.0


# ================= UNIVERSE LOADING =================

def detect_symbol_column(df: pd.DataFrame) -> str:
    """
    Detect symbol column in a schema-agnostic way.
    """
    normalized = {c.strip().lower(): c for c in df.columns}

    for key in ["symbol", "symbols", "ticker", "tickers"]:
        if key in normalized:
            return normalized[key]

    # fallback → first column
    return df.columns[0]


def load_universe() -> list:
    """
    Robust universe loader:
    • Case-insensitive
    • Whitespace safe
    • Works with any CSV schema
    """
    if not os.path.exists(UNIVERSE_FILE):
        raise FileNotFoundError("nifty200.csv missing in /data")

    df = pd.read_csv(UNIVERSE_FILE)

    if df.empty:
        raise ValueError("Universe CSV is empty")

    symbol_col = detect_symbol_column(df)

    symbols = (
        df[symbol_col]
        .astype(str)
        .str.strip()
        .str.upper()
        .dropna()
        .unique()
        .tolist()
    )

    if not symbols:
        raise ValueError("No valid symbols found in universe")

    log(f"Loaded universe: {len(symbols)} symbols")
    return sorted(symbols)


# ================= DATA DOWNLOAD =================

def download_prices(symbol: str):
    try:
        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if df is None or df.empty:
            return None

        close = df["Close"].dropna()

        if len(close) < MIN_PRICE_HISTORY:
            return None

        return close

    except Exception:
        return None


# ================= SIGNAL METRICS =================

def momentum(close: pd.Series, window: int) -> float:
    if close is None or len(close) < window:
        return 0.0
    try:
        return safe_float(close.iloc[-1] / close.iloc[-window] - 1)
    except Exception:
        return 0.0


def volatility(close: pd.Series) -> float:
    if close is None or len(close) < VOL_WINDOW:
        return 0.0

    try:
        vol_series = close.pct_change().rolling(VOL_WINDOW).std()
        if vol_series is None or vol_series.empty:
            return 0.0
        return safe_float(vol_series.iloc[-1])
    except Exception:
        return 0.0


def compute_signal(symbol: str, close: pd.Series):
    if close is None:
        return None

    moms = [momentum(close, w) for w in MOM_WINDOWS]
    vol = volatility(close)

    if vol <= 0:
        return None

    composite = float(np.mean(moms))
    strength = composite / vol if vol > 0 else 0.0

    return {
        "symbol": symbol,
        "momentum_1m": moms[0],
        "momentum_3m": moms[1],
        "momentum_6m": moms[2],
        "volatility": vol,
        "composite_momentum": composite,
        "signal_strength": strength,
    }


# ================= MAIN BUILDER =================

def build_signals() -> pd.DataFrame:
    log("Starting signal build...")

    symbols = load_universe()

    rows = []
    valid = 0
    rejected = 0

    for s in symbols:
        close = download_prices(s)
        row = compute_signal(s, close)

        if row:
            rows.append(row)
            valid += 1
        else:
            rejected += 1

    log(f"Valid symbols   : {valid}")
    log(f"Rejected symbols: {rejected}")

    if not rows:
        raise RuntimeError("No valid signals generated")

    df = pd.DataFrame(rows)

    df = df.sort_values("signal_strength", ascending=False).reset_index(drop=True)
    df = df.head(TOP_N_SIGNALS)

    log(f"Top signals selected: {len(df)}")
    return df


# ================= CLI =================

if __name__ == "__main__":
    log("=== SIGNAL ENGINE RUN ===")

    signals = build_signals()

    os.makedirs(DATA_PATH, exist_ok=True)
    out_file = os.path.join(DATA_PATH, "signals.csv")

    signals.to_csv(out_file, index=False)

    log(f"Signals saved → {out_file}")
    log("=== COMPLETE ===")
