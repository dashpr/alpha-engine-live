"""
Phase-2 Dashboard Enrichment Layer
Creates canonical investor-grade dashboard_data.json
WITHOUT changing UI layout.
"""

import os
import json
from datetime import datetime, date
import numpy as np
import pandas as pd

OUTPUT = "output"
CANONICAL = os.path.join(OUTPUT, "dashboard_data.json")


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def read_csv(path):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def iso_now():
    return datetime.utcnow().isoformat()


# ---------------- NAV + DRAWDOWN ---------------- #

def load_equity():
    csv_path = os.path.join(OUTPUT, "model_equity.csv")
    if not os.path.exists(csv_path):
        return [], []

    df = pd.read_csv(csv_path, parse_dates=[0])
    dates = df.iloc[:, 0].dt.strftime("%Y-%m-%d").tolist()
    values = df.iloc[:, 1].astype(float).tolist()
    return dates, values


def compute_performance(values):
    if len(values) < 2:
        return 0, [], 0

    arr = np.array(values)
    cumulative = (arr[-1] - arr[0]) / arr[0] * 100

    running_max = np.maximum.accumulate(arr)
    drawdown = (arr - running_max) / running_max * 100
    max_dd = float(drawdown.min())

    return float(round(cumulative, 2)), drawdown.tolist(), float(round(max_dd, 2))


def compute_risk(values):
    if len(values) < 2:
        return None, None

    arr = np.array(values)
    r = arr[1:] / arr[:-1] - 1

    vol = np.std(r) * np.sqrt(12) * 100
    sharpe = (np.mean(r) * 12 - 0.03) / (vol / 100) if vol != 0 else None

    return float(round(vol, 2)), float(round(sharpe, 2)) if sharpe else None


# ---------------- HOLDINGS ENRICHMENT ---------------- #

def enrich_holdings(holdings, prices, positions):
    rows = []

    for h in holdings:
        t = h.get("ticker")

        price = prices.get(f"{t}.NS", {}).get("price")
        change = prices.get(f"{t}.NS", {}).get("change_pct")

        pos = positions.get(f"{t}.NS", {})
        entry = pos.get("entry_price")
        qty = pos.get("quantity")

        value = price * qty if price and qty else None
        pnl = (price - entry) * qty if price and entry and qty else None
        pnl_pct = (pnl / (entry * qty) * 100) if pnl and entry and qty else None

        rows.append({
            "ticker": t,
            "weight_percent": h.get("weight"),
            "live_price": price,
            "daily_change_pct": change,
            "entry_price": entry,
            "quantity": qty,
            "position_value": value,
            "pnl_abs": pnl,
            "pnl_pct": pnl_pct
        })

    return rows


# ---------------- WATCHLIST HISTORY ---------------- #

def load_watchlist():
    df = read_csv(os.path.join(OUTPUT, "watchlist_history.csv"))
    if df.empty:
        return []

    return df.fillna("").to_dict("records")


# ---------------- REBALANCE ---------------- #

def days_until(date_str):
    if not date_str:
        return None
    d = datetime.fromisoformat(date_str).date()
    return (d - date.today()).days


# ---------------- MAIN ---------------- #

def main():

    raw = read_json(os.path.join(OUTPUT, "dashboard_data.json"))
    prices = read_json(os.path.join(OUTPUT, "prices_live.json"))
    positions = read_json(os.path.join(OUTPUT, "portfolio_positions.json"))
    ai_summary = read_json(os.path.join(OUTPUT, "ai_summary.json"))

    # NAV
    dates, values = load_equity()
    cumulative, drawdown, max_dd = compute_performance(values)
    vol, sharpe = compute_risk(values)

    # Holdings
    holdings = enrich_holdings(raw.get("holdings", []), prices, positions)

    # Watchlist
    watchlist_history = load_watchlist()

    # Rebalance
    last_reb = read_json(os.path.join(OUTPUT, "last_rebalance.json")).get("date")
    next_reb = read_json(os.path.join(OUTPUT, "next_rebalance.json")).get("date")
    next_days = days_until(next_reb)

    # CIO
    cio = ai_summary.get("summary", "CIO commentary unavailable.")

    payload = {
        "timestamp": iso_now(),
        "equity_dates": dates,
        "equity_values": values,
        "drawdown_series": drawdown,
        "cumulative_return_pct": cumulative,
        "max_drawdown_pct": max_dd,
        "volatility_pct": vol,
        "sharpe": sharpe,
        "holdings": holdings,
        "watchlist_history": watchlist_history,
        "trades": raw.get("trades", []),
        "regime": raw.get("regime"),
        "last_rebalance": last_reb,
        "next_rebalance": next_reb,
        "next_rebalance_days": next_days,
        "cio_commentary": cio
    }

    os.makedirs(OUTPUT, exist_ok=True)
    with open(CANONICAL, "w") as f:
        json.dump(payload, f, indent=2)

    print("Dashboard enriched successfully.")


if __name__ == "__main__":
    main()
