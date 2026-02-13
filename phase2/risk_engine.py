import json
import pandas as pd
import numpy as np
from datetime import datetime

NAV_FILE = "phase2/data/nav.json"
HIST_FILE = "phase2/data/nav_history.csv"
RISK_FILE = "phase2/data/risk.json"

ROLL = 126
YEAR = 252


def load_nav():
    with open(NAV_FILE) as f:
        return json.load(f)["value"]


def update_hist(nav):
    try:
        df = pd.read_csv(HIST_FILE)
    except:
        df = pd.DataFrame(columns=["date", "nav"])

    today = datetime.utcnow().date()
    if len(df) == 0 or pd.to_datetime(df.iloc[-1]["date"]).date() != today:
        df.loc[len(df)] = [today, nav]

    df.to_csv(HIST_FILE, index=False)
    return df


def compute(df):
    if len(df) < ROLL:
        return {"cagr": 0, "max_dd": 0, "volatility": 0, "sharpe": 0, "regime": "WARMUP"}

    d = df.tail(ROLL).copy()
    d["ret"] = d["nav"].pct_change()

    total = d["nav"].iloc[-1] / d["nav"].iloc[0]
    cagr = total ** (YEAR / len(d)) - 1
    vol = d["ret"].std() * np.sqrt(YEAR)
    sharpe = cagr / (vol + 1e-9)

    dd = (d["nav"] / d["nav"].cummax() - 1).min()

    regime = "RISK_ON" if sharpe > 1 and dd > -0.1 else "NEUTRAL" if sharpe > 0 else "RISK_OFF"

    return {
        "cagr": round(cagr * 100, 2),
        "max_dd": round(dd * 100, 2),
        "volatility": round(vol * 100, 2),
        "sharpe": round(sharpe, 2),
        "regime": regime,
    }


def run():
    nav = load_nav()
    hist = update_hist(nav)
    risk = compute(hist)
    risk["timestamp"] = datetime.utcnow().isoformat()

    with open(RISK_FILE, "w") as f:
        json.dump(risk, f, indent=2)

    print("Risk updated:", risk["regime"])
