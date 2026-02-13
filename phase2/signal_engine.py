"""
PHASE-2 INSTITUTIONAL SIGNAL ENGINE
-----------------------------------

Responsibilities:
• Download price data for NIFTY-200 universe
• Compute multi-horizon momentum
• Compute scalar-safe volatility
• Rank securities deterministically
• Output clean signal dataframe for portfolio constructor

Design Principles:
• CI-safe pandas handling
• Deterministic outputs
• Zero-crash guarantees
• Institutional logging clarity
"""

import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# ================= CONFIG =================

DATA_PATH = "data"
UNIVERSE_FILE = os.path.join(DATA_PATH, "nifty200.csv")

LOOKBACK_DAYS = 252
MOM_WINDOWS = [21, 63, 126]
VOL_WINDOW = 63

MIN_PRICE_HISTORY = 150
TOP_N_SIGNALS = 30


# ================= UTILITIES =================

def log(msg: str):
    """Simple deterministic logger."""
    print(f"[SIGNAL_ENGINE] {msg}")


def safe_float(value) -> float:
    """
    Convert pandas/numpy/scalar safely to float.
    Never throws.
    """
    try:
        if hasattr(value, "item"):
            return float(value.item())
        return float(value)
    except Exception:
        return 0.0


# ================= DATA LOADING =================

def load_universe() -> list:
    """Load NIFTY-200 symbols."""
    if not os.path.exists(UNIVERSE_FILE):
        raise FileNotFoundError("nifty200.csv not found in /data")

    df = pd.read_csv(UNIVERSE_FILE)

    if "Symbol" not in df.columns:
        raise ValueError("Universe file must contain 'Symbol' column")

    symbols = sorted(df["Symbol"].dropna().unique().tolist())

    log(f"Loaded universe: {len(symbols)} symbols")
    return symbols


def download_prices(symbol: str) -> pd.Series | None:
    """
    Download adjusted close prices from Yahoo Finance.
    Returns None if invalid or insufficient data.
    """
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


# ================= SIGNAL CALCULATIONS =================

def momentum(close: pd.Series, window: int) -> float:
    """Compute scalar-safe momentum."""
    if close is None or len(close) < window:
        return 0.0

    try:
        return safe_float(close.iloc[-1] / close.iloc[-window] - 1)
    except Exception:
        return 0.0


def volatility(close: pd.Series) -> float:
    """
    Scalar-safe rolling volatility.
    GUARANTEED never to crash CI.
    """
    if close is None or len(close) < VOL_WINDOW:
        return 0.0

    try:
        vol_series = close.pct_change().rolling(VOL_WINDOW).std()

        if vol_series is None or vol_series.empty:
            return 0.0

        last_val = vol_series.iloc[-1]
        return safe_float(last_val)

    except Exception:
        return 0.0


def compute_signal_row(symbol: str, close: pd.Series) -> dict | None:
    """Build signal metrics for one stock."""
    if close is None:
        return None

    mom_scores = [momentum(close, w) for w in MOM_WINDOWS]
    vol = volatility(close)

    # Reject zero-vol assets (bad data)
    if vol <= 0:
        return None

    # Institutional composite momentum score
    composite_mom = np.mean(mom_scores)

    # Risk-adjusted signal
    signal_strength = composite_mom / vol if vol > 0 else 0.0

    return {
        "symbol": symbol,
        "momentum_1m": mom_scores[0],
        "momentum_3m": mom_scores[1],
        "momentum_6m": mom_scores[2],
        "volatility": vol,
        "composite_momentum": composite_mom,
        "signal_strength": signal_strength,
    }


# ================= MAIN ENGINE =================

def build_signals() -> pd.DataFrame:
    """
    Institutional deterministic signal builder.
    Produces ranked dataframe ready for portfolio construction.
    """
    log("Starting signal build...")

    symbols = load_universe()

    rows = []
    valid = 0
    rejected = 0

    for symbol in symbols:
        close = download_prices(symbol)

        row = compute_signal_row(symbol, close)

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

    # Deterministic ranking
    df = df.sort_values("signal_strength", ascending=False).reset_index(drop=True)

    # Keep only top signals
    df = df.head(TOP_N_SIGNALS)

    log(f"Top signals selected: {len(df)}")

    return df


# ================= CLI ENTRY =================

if __name__ == "__main__":
    log("=== PHASE-2 SIGNAL ENGINE RUN ===")

    signals = build_signals()

    os.makedirs(DATA_PATH, exist_ok=True)

    out_file = os.path.join(DATA_PATH, "signals.csv")
    signals.to_csv(out_file, index=False)

    log(f"Signals saved → {out_file}")
    log("=== SIGNAL ENGINE COMPLETE ===")
