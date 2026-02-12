#!/usr/bin/env python3
# CLOUD_ALPHA_RUNNER.py
# Minimal, robust runner that writes required output files for the dashboard.
# Replace the mock sections with your real engine outputs as needed.

import json
import datetime
from pathlib import Path
import csv

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

def safe_write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    tmp.replace(path)

def iso_now():
    return datetime.datetime.now().strftime("%d %b %Y %I:%M %p IST")

try:
    # >>> Replace these mock variables with your actual engine outputs <<<
    # Example placeholders (safe defaults)
    last_rebalance_date = datetime.date.today().isoformat()
    # next rebalance = last day of next month (simple heuristic)
    today = datetime.date.today()
    next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    next_rebalance_date = next_month.isoformat()

    ai_text = "Market breadth improving while volatility remains contained. Momentum leadership in large caps persists."
    headlines_list = [
        "Reliance outlook supported by refining margin strength",
        "Bank credit growth trends remain positive",
        "IT sector commentary indicates cautious recovery"
    ]
    timestamp = iso_now()

    # Write required JSON outputs
    safe_write_json(OUTPUT / "last_rebalance.json", {"date": last_rebalance_date})
    safe_write_json(OUTPUT / "next_rebalance.json", {"date": next_rebalance_date})
    safe_write_json(OUTPUT / "last_updated.json", {"timestamp": timestamp})
    safe_write_json(OUTPUT / "ai_summary.json", {"summary": ai_text, "timestamp": timestamp})
    safe_write_json(OUTPUT / "headlines.json", headlines_list)

    # Write a watchlist_history.csv (header + sample rows)
    watch_csv = OUTPUT / "watchlist_history.csv"
    with watch_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "included_on", "exited_on", "reason"])
        writer.writerow(["RELIANCE", "2025-06-01", "", "Momentum entry"])
        writer.writerow(["INFY", "2025-07-01", "2025-12-01", "Rank drop"])

    print("CLOUD_ALPHA_RUNNER: outputs written to 'output/' successfully.")
    # Exit 0 so workflow continues (the commit step handles if nothing changed)
    raise SystemExit(0)

except Exception as e:
    # Log the error to console and write a minimal fail-safe output, then exit non-zero
    print("CLOUD_ALPHA_RUNNER: ERROR:", str(e))
    # write an error file for debugging
    safe_write_json(OUTPUT / "runner_error.json", {"error": str(e), "timestamp": iso_now()})
    raise
