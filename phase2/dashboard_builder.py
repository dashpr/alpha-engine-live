"""
PHASE-2 DASHBOARD BUILDER (ROOT-LEVEL GITHUB PAGES)
---------------------------------------------------

Creates canonical dashboard JSON at repository root:

    data.json  ← served by GitHub Pages

Also keeps archive copy in:

    output/dashboard_data.json
"""

import os
import json
import pandas as pd
from datetime import datetime


DATA_PATH = "data"
OUTPUT_PATH = "output"

ROOT_JSON = "data.json"
ARCHIVE_JSON = os.path.join(OUTPUT_PATH, "dashboard_data.json")


def log(msg: str):
    print(f"[DASHBOARD] {msg}")


def read_csv_safe(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def build_payload() -> dict:
    signals = read_csv_safe(os.path.join(DATA_PATH, "signals.csv"))
    portfolio = read_csv_safe(os.path.join(DATA_PATH, "portfolio.csv"))
    nav = read_csv_safe(os.path.join(DATA_PATH, "nav.csv"))
    risk = read_csv_safe(os.path.join(DATA_PATH, "risk.csv"))
    commentary = read_csv_safe(os.path.join(DATA_PATH, "commentary.csv"))

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "signals": signals.to_dict(orient="records"),
        "portfolio": portfolio.to_dict(orient="records"),
        "nav": nav.to_dict(orient="records"),
        "risk": risk.to_dict(orient="records"),
        "commentary": commentary.to_dict(orient="records"),
        "watchlist_past": [],
        "rebalance": {"last": "NA", "next_days": "NA"},
    }

    return payload


def save_json(payload: dict):
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # 1️⃣ Canonical GitHub Pages JSON
    with open(ROOT_JSON, "w") as f:
        json.dump(payload, f, indent=2)

    # 2️⃣ Archive copy
    with open(ARCHIVE_JSON, "w") as f:
        json.dump(payload, f, indent=2)

    log(f"Saved root JSON → {ROOT_JSON}")
    log(f"Saved archive   → {ARCHIVE_JSON}")


def build_dashboard():
    log("Building dashboard payload...")
    payload = build_payload()
    save_json(payload)
    log("Dashboard build complete.")


if __name__ == "__main__":
    build_dashboard()
