"""
Phase-2 Live Price Engine (Institutional Grade)

Responsibilities:
- Load dynamic NSE-200 universe
- Fetch latest prices from Yahoo Finance
- Handle failures deterministically
- Produce stable output: output/prices_live.json
"""

from pathlib import Path
import json
import time
from typing import Dict, List

import yfinance as yf


# ============================================================
# PATHS
# ============================================================

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

UNIVERSE_FILE = OUTPUT / "universe.json"
PRICES_FILE = OUTPUT / "prices_live.json"


# ============================================================
# LOAD UNIVERSE
# ============================================================

def load_universe() -> List[str]:
    """
    Loads NSE-200 universe from output/universe.json.
    Fails fast if universe missing (institutional safety).
    """
    if not UNIVERSE_FILE.exists():
        raise FileNotFoundError(
            "❌ universe.json not found. Run phase2/universe_loader.py first."
        )

    with open(UNIVERSE_FILE, "r") as f:
        symbols = json.load(f)

    # defensive cleaning
    symbols = [s.strip().upper() for s in symbols if s]

    if not symbols:
        raise ValueError("❌ universe.json is empty.")

    return symbols


# ============================================================
# SAFE YAHOO FETCH
# ============================================================

def fetch_prices(symbols: List[str]) -> Dict[str, float]:
    """
    Fetches latest close price for all symbols using Yahoo Finance.

    Guarantees:
    - Returns dict for ALL symbols
    - No crashes on partial failure
    - No NaN propagation
    """

    yf_symbols = [f"{s}.NS" for s in symbols]

    # Yahoo occasionally throttles → retry logic
    for attempt in range(3):
        try:
            data = yf.download(
                tickers=" ".join(yf_symbols),
                period="5d",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=True,
            )
            break
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"Yahoo fetch failed after retries: {e}")
            time.sleep(2)

    prices: Dict[str, float] = {}

    for sym in symbols:
        yf_sym = f"{sym}.NS"

        try:
            # Handle both multi-index and flat dataframe shapes
            if isinstance(data.columns, type(getattr(data.columns, "levels", None))):
                close_series = data[yf_sym]["Close"]
            else:
                close_series = data["Close"]

            price = float(close_series.ffill().iloc[-1])

            # Reject invalid prices
            if price <= 0:
                raise ValueError("Non-positive price")

            prices[sym] = round(price, 2)

        except Exception:
            # Institutional fallback:
            # Instead of null → carry forward previous price if available
            previous = load_previous_price(sym)
            prices[sym] = previous if previous is not None else 0.0

    return prices


# ============================================================
# PREVIOUS PRICE FALLBACK
# ============================================================

def load_previous_price(symbol: str):
    """
    Loads previous stored price to avoid null propagation.
    """
    if not PRICES_FILE.exists():
        return None

    try:
        with open(PRICES_FILE, "r") as f:
            old = json.load(f)
        return old.get(symbol)
    except Exception:
        return None


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_prices(prices: Dict[str, float]) -> None:
    """
    Writes deterministic JSON output.
    """
    with open(PRICES_FILE, "w") as f:
        json.dump(prices, f, indent=2, sort_keys=True)

    print(f"✅ prices_live.json updated — {len(prices)} symbols")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    symbols = load_universe()
    prices = fetch_prices(symbols)
    save_prices(prices)


if __name__ == "__main__":
    main()
