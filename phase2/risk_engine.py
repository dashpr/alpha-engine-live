import json
import pandas as pd
import numpy as np
from datetime import datetime

NAV_FILE = "phase2/data/nav.json"
HISTORY_FILE = "phase2/data/nav_history.csv"
RISK_FILE = "phase2/data/risk.json"

ROLLING_DAYS = 126  # ≈ 6 months trading days
TRADING_DAYS_YEAR = 252


# =========================
# LOAD NAV
# =========================
def load_nav():
    with open(NAV_FILE) as f:
        return json.load(f)["value"]


# =========================
# UPDATE NAV HISTORY
# =========================
def update_history(nav_value: float):

    try:
        hist = pd.read_csv(HISTORY_FILE)
    except FileNotFoundError:
        hist = pd.DataFrame(columns=["date", "nav"])

    today = datetime.utcnow().date()

    if len(hist) == 0 or pd.to_datetime(hist.iloc[-1]["date"]).date() != today:
        hist.loc[len(hist)] = [today, nav_value]

    hist.to_csv(HISTORY_FILE, index=False)
    return hist


# =========================
# RISK METRICS
# =========================
def compute_risk(hist: pd.DataFrame):

    if len(hist) < ROLLING_DAYS:
        return {
            "cagr": 0,
            "max_dd": 0,
            "volatility": 0,
            "sharpe": 0,
            "regime": "WARMUP"
        }

    df = hist.tail(ROLLING_DAYS).copy()
    df["returns"] = df["nav"].pct_change()

    # CAGR
    total_return = df["nav"].iloc[-1] / df["nav"].iloc[0]
    cagr = total_return ** (TRADING_DAYS_YEAR / len(df)) - 1

    # Volatility
    vol = df["returns"].std() * np.sqrt(TRADING_DAYS_YEAR)

    # Sharpe (risk-free ≈ 0 for simplicity)
    sharpe = cagr / (vol + 1e-9)

    # Max drawdown
    rolling_max = df["nav"].cummax()
    dd = df["nav"] / rolling_max - 1
    max_dd = dd.min()

    # Regime classification
    if sharpe > 1 and max_dd > -0.1:
        regime = "RISK_ON"
    elif sharpe > 0:
        regime = "NEUTRAL"
    else:
        regime = "RISK_OFF"

    return {
        "cagr": round(cagr * 100, 2),
        "max_dd": round(max_dd * 100, 2),
        "volatility": round(vol * 100, 2),
        "sharpe": round(sharpe, 2),
        "regime": regime
    }


# =========================
# MAIN
# =========================
def run():

    nav_value = load_nav()
    hist = update_history(nav_value)
    risk = compute_risk(hist)

    risk["timestamp"] = datetime.utcnow().isoformat()

    with open(RISK_FILE, "w") as f:
        json.dump(risk, f, indent=2)

    print("Risk engine updated:", risk)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run()
