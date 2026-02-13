"""
PHASE-2 INSTITUTIONAL DASHBOARD BUILDER
--------------------------------------

Creates deterministic dashboard JSON for investor UI.

Output:
dashboard/data.json
"""

import os
import json
import pandas as pd
from datetime import datetime


DATA_PATH = "data"
DASHBOARD_PATH = "dashboard"
OUTPUT_FILE = os.path.join(DASHBOARD_PATH, "data.json")


def log(msg: str):
    print(f"[DASHBOARD] {msg}")


def safe_read_csv(path: str) -> pd.DataFrame:
    """Read CSV safely. Returns empty DF if missing."""
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def build_dashboard_payload() -> dict:
    """
    Assemble full institutional dashboard payload.
    """

    signals = safe_read_csv(os.path.join(DATA_PATH, "signals.csv"))
    portfolio = safe_read_csv(os.path.join(DATA_PATH, "portfolio.csv"))
    nav = safe_read_csv(os.path.join(DATA_PATH, "nav.csv"))
    risk = safe_read_csv(os.path.join(DATA_PATH, "risk.csv"))
    commentary = safe_read_csv(os.path.join(DATA_PATH, "commentary.csv"))

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "signals": signals.to_dict(orient="records"),
        "portfolio": portfolio.to_dict(orient="records"),
        "nav": nav.to_dict(orient="records"),
        "risk": risk.to_dict(orient="records"),
        "commentary": commentary.to_dict(orient="records"),
    }

    return payload


def save_dashboard_json(payload: dict):
    os.makedirs(DASHBOARD_PATH, exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    log(f"Dashboard JSON saved → {OUTPUT_FILE}")


def build_dashboard():
    log("Building dashboard payload...")
    payload = build_dashboard_payload()
    save_dashboard_json(payload)
    log("Dashboard build complete.")


if __name__ == "__main__":
    build_dashboard()
