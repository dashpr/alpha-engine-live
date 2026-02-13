"""
PHASE-2 DASHBOARD BUILDER (FINAL CONTRACT)
------------------------------------------

Reads engine outputs and writes canonical dashboard JSON to:

    dashboard/data.json   ← GitHub Pages source

Also keeps optional archival copy in:

    output/dashboard_data.json
"""

import os
import json
import pandas as pd
from datetime import datetime


DATA_PATH = "data"
OUTPUT_PATH = "output"
DASHBOARD_DIR = "dashboard"

CANONICAL_JSON = os.path.join(DASHBOARD_DIR, "data.json")
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
    # Ensure directories exist
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # 1️⃣ Canonical JSON for dashboard
    with open(CANONICAL_JSON, "w") as f:
        json.dump(payload, f, indent=2)

    # 2️⃣ Archive JSON (existing behavior preserved)
    with open(ARCHIVE_JSON, "w") as f:
        json.dump(payload, f, indent=2)

    log(f"Saved canonical → {CANONICAL_JSON}")
    log(f"Saved archive   → {ARCHIVE_JSON}")


def build_dashboard():
    log("Building dashboard payload...")
    payload = build_payload()
    save_json(payload)
    log("Dashboard build complete.")


if __name__ == "__main__":
    build_dashboard()
