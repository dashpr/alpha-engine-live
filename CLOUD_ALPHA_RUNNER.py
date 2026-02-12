import json
import datetime
import pathlib
import pandas as pd


OUTPUT = pathlib.Path("output")
OUTPUT.mkdir(exist_ok=True)


# --- MOCK DATA (replace with real engine outputs later) ---
last_rebalance_date = datetime.date.today().replace(day=1)
next_rebalance_date = (last_rebalance_date + datetime.timedelta(days=32)).replace(day=1)


ai_text = "Market breadth improving while volatility remains contained. Momentum leadership in large caps persists."
headlines_list = [
"Reliance outlook supported by refining margin strength",
"Bank credit growth trends remain positive",
"IT sector commentary indicates cautious recovery"
]


now = datetime.datetime.now().strftime("%d %b %Y %I:%M %p IST")


# --- WRITE JSON OUTPUTS ---
(OUTPUT / "last_rebalance.json").write_text(json.dumps({"date": str(last_rebalance_date)}))
(OUTPUT / "next_rebalance.json").write_text(json.dumps({"date": str(next_rebalance_date)}))
(OUTPUT / "last_updated.json").write_text(json.dumps({"timestamp": now}))
(OUTPUT / "ai_summary.json").write_text(json.dumps({"summary": ai_text, "timestamp": now}))
(OUTPUT / "headlines.json").write_text(json.dumps(headlines_list))


# --- WATCHLIST HISTORY SAMPLE ---
watchlist = pd.DataFrame([
["RELIANCE", "2025-06-01", "", "Momentum entry"],
["INFY", "2025-07-01", "2025-12-01", "Rank drop"],
], columns=["symbol", "included_on", "exited_on", "reason"])


watchlist.to_csv(OUTPUT / "watchlist_history.csv", index=False)


print("Alpha runner outputs refreshed.")
