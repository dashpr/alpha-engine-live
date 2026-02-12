#!/usr/bin/env python3
import json
import datetime
from pathlib import Path
import csv


OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)


def write_json(path, data):
with open(path, "w", encoding="utf-8") as f:
json.dump(data, f, indent=2)


now = datetime.datetime.now()


last_rebalance = now.date().isoformat()
next_rebalance = (now.date().replace(day=28) + datetime.timedelta(days=4)).replace(day=1).isoformat()


timestamp = now.strftime("%d %b %Y %I:%M %p IST")


ai_summary = "Market breadth improving while volatility remains contained. Momentum leadership in large caps persists."


headlines = [
"Reliance outlook supported by refining margin strength",
"Bank credit growth trends remain positive",
"IT sector commentary indicates cautious recovery"
]


write_json(OUTPUT / "last_rebalance.json", {"date": last_rebalance})
write_json(OUTPUT / "next_rebalance.json", {"date": next_rebalance})
write_json(OUTPUT / "last_updated.json", {"timestamp": timestamp})
write_json(OUTPUT / "ai_summary.json", {"summary": ai_summary, "timestamp": timestamp})
write_json(OUTPUT / "headlines.json", headlines)


with open(OUTPUT / "watchlist_history.csv", "w", newline="", encoding="utf-8") as f:
writer = csv.writer(f)
writer.writerow(["symbol", "included_on", "exited_on", "reason"])
writer.writerow(["RELIANCE", "2025-06-01", "", "Momentum entry"])
writer.writerow(["INFY", "2025-07-01", "2025-12-01", "Rank drop"])


print("Alpha runner completed successfully")
