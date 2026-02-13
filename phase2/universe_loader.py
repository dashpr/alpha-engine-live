"""
Dynamic NSE-200 universe loader
No static CSV dependency.
"""

import pandas as pd
from pathlib import Path
import requests

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

NSE200_URL = "https://archives.nseindia.com/content/indices/ind_nifty200list.csv"


def fetch_nse200():
    df = pd.read_csv(NSE200_URL)
    symbols = df["Symbol"].dropna().unique().tolist()

    with open(OUTPUT / "universe.json", "w") as f:
        import json
        json.dump(symbols, f, indent=2)

    print(f"✅ NSE-200 universe loaded: {len(symbols)} stocks")


if __name__ == "__main__":
    fetch_nse200()
