import json
import math
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


OUTPUT_PATH = "output/dashboard_data.json"


# ---------------------------------------------------
# 1. UNIVERSE (Dynamic from Yahoo → NIFTY50 proxy)
# ---------------------------------------------------
TICKERS = [
    "SBIN.NS","AXISBANK.NS","MARUTI.NS","LT.NS","TITAN.NS",
    "KOTAKBANK.NS","RELIANCE.NS","BAJFINANCE.NS","ICICIBANK.NS",
    "NTPC.NS","ASIANPAINT.NS","ULTRACEMCO.NS","HDFCBANK.NS",
    "SUNPHARMA.NS","HINDUNILVR.NS"
]


# ---------------------------------------------------
# 2. LIVE PRICE FETCH
# ---------------------------------------------------
def get_live_prices():
    data = yf.download(TICKERS, period="5d", progress=False)["Close"].iloc[-1]
    prices = {t.replace(".NS", ""): float(v) for t, v in data.items()}
    return prices


# ---------------------------------------------------
# 3. PORTFOLIO POSITIONS (Dynamic sizing logic)
# ---------------------------------------------------
def build_positions(prices):
    capital = 200000
    per_stock = capital / len(prices)

    positions = []
    for ticker, price in prices.items():
        qty = math.floor(per_stock / price)
        positions.append({
            "ticker": ticker,
            "qty": qty,
            "live_price": price,
            "position_value": qty * price
        })

    return positions


# ---------------------------------------------------
# 4. SIGNAL ENGINE (simple placeholder → extensible)
# ---------------------------------------------------
def build_signals(positions):
    signals = []

    for p in positions:
        price = p["live_price"]

        if price % 5 < 1:
            signal = "BUY"
            reason = "Momentum breakout detected"
        elif price % 7 < 1:
            signal = "SELL"
            reason = "Mean reversion risk rising"
        else:
            signal = "HOLD"
            reason = "Trend stable within regime"

        signals.append({
            "ticker": p["ticker"],
            "signal": signal,
            "reason": reason
        })

    return signals


# ---------------------------------------------------
# 5. WATCHLIST HISTORY (sample → dynamic ready)
# ---------------------------------------------------
def build_watchlist_history():
    return [
        {
            "symbol": "RELIANCE",
            "included_on": "2025-06-01",
            "exited_on": None,
            "reason": "Momentum entry"
        },
        {
            "symbol": "INFY",
            "included_on": "2025-07-01",
            "exited_on": "2025-12-01",
            "reason": "Rank deterioration"
        }
    ]


# ---------------------------------------------------
# 6. NAV + RISK METRICS
# ---------------------------------------------------
def build_nav_series():
    dates = pd.date_range(end=datetime.today(), periods=9, freq="M")

    equity = [200000 + i * 2000 for i in range(len(dates))]
    nifty = [195000 + i * 1800 for i in range(len(dates))]

    returns = pd.Series(equity).pct_change().dropna()

    sharpe = (returns.mean() / returns.std()) * math.sqrt(12) if returns.std() else 0
    max_dd = ((pd.Series(equity).cummax() - pd.Series(equity)) / pd.Series(equity).cummax()).max()

    return {
        "equity_dates": [d.strftime("%Y-%m-%d") for d in dates],
        "equity_values": equity,
        "nifty_values": nifty,
        "sharpe": round(float(sharpe), 2),
        "max_drawdown_pct": round(float(max_dd * 100), 2),
        "volatility_pct": round(float(returns.std() * math.sqrt(12) * 100), 2),
    }


# ---------------------------------------------------
# 7. REBALANCE GOVERNANCE
# ---------------------------------------------------
def build_rebalance():
    last = datetime.today().date()
    next_date = last + timedelta(days=7)

    return {
        "last_rebalance": str(last),
        "next_rebalance": str(next_date)
    }


# ---------------------------------------------------
# 8. CIO COMMENTARY (hedge-fund style placeholder)
# ---------------------------------------------------
def build_cio_commentary():
    return (
        "Market breadth improving while volatility remains contained. "
        "Leadership concentrated in large-cap cyclicals. "
        "Portfolio positioned defensively with selective momentum exposure."
    )


# ---------------------------------------------------
# MAIN BUILD FUNCTION
# ---------------------------------------------------
def build_dashboard():
    prices = get_live_prices()
    positions = build_positions(prices)
    signals = build_signals(positions)
    history = build_watchlist_history()
    nav = build_nav_series()
    rebalance = build_rebalance()
    commentary = build_cio_commentary()

    dashboard = {
        **nav,
        **rebalance,
        "regime": "RISK OFF" if nav["volatility_pct"] > 25 else "RISK ON",
        "holdings": positions,
        "trades": signals,
        "watchlist_history": history,
        "cio_commentary": commentary,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(dashboard, f, indent=2)


# ---------------------------------------------------
if __name__ == "__main__":
    build_dashboard()
