# =============================================
# CLOUD_ALPHA_RUNNER.py
# Final cloud execution engine for Alpha System
# =============================================

import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime, timedelta

# ---------------- CONFIG ----------------
START_CAPITAL = 200000
TOP_N = 15
TXN_COST = 0.004
DATA_PERIOD = "20y"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ---------------- LOAD NIFTY (robust) ----------------
def load_nifty():
    for _ in range(3):  # retry download
        try:
            nifty = yf.download("^NSEI", period=DATA_PERIOD, progress=False)

            if nifty is None or nifty.empty:
                continue

            close = nifty["Close"]

            if close.empty:
                continue

            dma200 = close.rolling(200).mean()
            risk_on = close > dma200

            return pd.DataFrame({"Close": close, "RiskOn": risk_on})

        except Exception:
            continue

    # fallback safe dataframe
    dates = pd.date_range(end=datetime.today(), periods=300)
    close = pd.Series(np.nan, index=dates)
    risk_on = pd.Series(False, index=dates)

    return pd.DataFrame({"Close": close, "RiskOn": risk_on})


# ---------------- STOCK UNIVERSE ----------------
TICKERS = [
    "RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
    "LT.NS","SBIN.NS","ITC.NS","HINDUNILVR.NS","BAJFINANCE.NS",
    "KOTAKBANK.NS","ASIANPAINT.NS","AXISBANK.NS","MARUTI.NS","SUNPHARMA.NS",
    "TITAN.NS","ULTRACEMCO.NS","WIPRO.NS","NTPC.NS","POWERGRID.NS"
]


# ---------------- LOAD PRICES ----------------
def load_prices():
    data = yf.download(TICKERS, period=DATA_PERIOD, progress=False)["Close"]
    return data.dropna(how="all")


# ---------------- MOMENTUM SCORE ----------------
def compute_momentum(prices):

    mom12 = prices.pct_change(252)
    mom1 = prices.pct_change(21)
    mom6 = prices.pct_change(126)
    vol = prices.pct_change().rolling(63).std()

    mom12_skip1 = mom12 - mom1

    score = (
        mom12_skip1.rank(axis=1, pct=True) * 0.5
        + mom6.rank(axis=1, pct=True) * 0.3
        + (-vol).rank(axis=1, pct=True) * 0.2
    )

    return score


# ---------------- DUMMY QUALITY ----------------
def dummy_quality(prices):
    return pd.Series(0.5, index=prices.columns)


# ---------------- BACKTEST CORE ----------------
def backtest(prices, scores, nifty, quality):

    monthly_dates = prices.resample("ME").last().index

    capital = START_CAPITAL
    equity_curve = []

    for i in range(2, len(monthly_dates)):

        signal_month = monthly_dates[i - 2]
        trade_start = monthly_dates[i - 1]
        trade_end = monthly_dates[i]

        score_date = scores.index[scores.index <= signal_month].max()
        start_date = prices.index[prices.index <= trade_start].max()
        end_date = prices.index[prices.index <= trade_end].max()
        nifty_date = nifty.index[nifty.index <= signal_month].max()

        if pd.isna(score_date) or pd.isna(start_date) or pd.isna(end_date):
            continue

        if not nifty.loc[nifty_date, "RiskOn"]:
            equity_curve.append((trade_end, capital))
            continue

        momentum_rank = scores.loc[score_date].dropna()

        combined = (
            momentum_rank.rank(pct=True) * 0.6
            + quality.reindex(momentum_rank.index).fillna(0) * 0.4
        )

        top = combined.nlargest(TOP_N).index

        start_prices = prices.loc[start_date, top]
        end_prices = prices.loc[end_date, top]

        valid = (~start_prices.isna()) & (~end_prices.isna())
        if valid.sum() == 0:
            equity_curve.append((trade_end, capital))
            continue

        returns = (end_prices[valid] / start_prices[valid]) - 1
        portfolio_return = returns.mean() - TXN_COST

        capital *= 1 + portfolio_return
        equity_curve.append((trade_end, capital))

    equity_df = pd.DataFrame(equity_curve, columns=["Date", "Equity"]).set_index("Date")
    return equity_df


# ---------------- EXECUTION SIGNALS ----------------
def execution_signals(prices, latest_top):

    signals = []

    for ticker in latest_top:
        series = prices[ticker].dropna()

        if len(series) < 120:
            continue

        price = series.iloc[-1]
        high20 = series.rolling(20).max().iloc[-1]
        dma50 = series.rolling(50).mean().iloc[-1]
        dma100 = series.rolling(100).mean().iloc[-1]

        if price < high20 * 0.95 and price > dma50:
            signal = "BUY NOW"
        elif price > dma50 * 1.15:
            signal = "WAIT"
        elif price > dma100 * 1.25:
            signal = "TRIM"
        else:
            signal = "HOLD"

        signals.append({"ticker": ticker.replace(".NS", ""), "signal": signal})

    return signals


# ---------------- MAIN ----------------
def main():

    print("Running cloud alpha engine...")

    prices = load_prices()
    nifty = load_nifty()

    scores = compute_momentum(prices)
    quality = dummy_quality(prices)

    equity = backtest(prices, scores, nifty, quality)

    latest_scores = scores.iloc[-1].dropna()
    top = latest_scores.nlargest(TOP_N).index

    signals = execution_signals(prices, top)

    dashboard = {
        "regime": "RISK ON" if nifty["RiskOn"].iloc[-1] else "RISK OFF",
        "last_rebalance": str(equity.index[-1].date()),
        "next_rebalance": str((equity.index[-1] + timedelta(days=30)).date()),
        "equity_dates": [d.strftime("%Y-%m-%d") for d in equity.index[-200:]],
        "equity_values": equity["Equity"].tail(200).round(2).tolist(),
        "nifty_values": nifty["Close"].reindex(equity.index).ffill().tail(200).round(2).tolist(),
        "holdings": [{"ticker": t.replace(".NS", ""), "weight": round(100 / TOP_N, 2)} for t in top],
        "trades": signals,
    }

    with open(os.path.join(OUTPUT_DIR, "dashboard_data.json"), "w") as f:
        json.dump(dashboard, f, indent=2)

    equity.to_csv(os.path.join(OUTPUT_DIR, "model_equity.csv"))

    print("Cloud run complete. Files updated.")


if __name__ == "__main__":
    main()
