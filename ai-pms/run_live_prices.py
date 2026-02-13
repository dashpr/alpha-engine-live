import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime


UNIVERSE_PATH = Path("data/input/universe.csv")
OUTPUT_PATH = Path("data/input/prices_live.json")


def load_universe():
    if not UNIVERSE_PATH.exists():
        raise FileNotFoundError(
            f"Universe file not found at {UNIVERSE_PATH}. "
            "Please add data/input/universe.csv with a 'symbol' column."
        )

    df = pd.read_csv(UNIVERSE_PATH)

    if "symbol" not in df.columns:
        raise ValueError("universe.csv must contain a 'symbol' column.")

    return df["symbol"].dropna().unique().tolist()


def fetch_prices(symbols):
    all_data = []

    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")

            if hist.empty:
                continue

            hist = hist.reset_index()[["Date", "Close"]]
            hist.columns = ["date", "close"]
            hist["symbol"] = symbol

            all_data.append(hist)

        except Exception:
            continue

    if not all_data:
        raise RuntimeError("No price data fetched from Yahoo Finance.")

    df = pd.concat(all_data, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])

    return df.sort_values(["symbol", "date"])


def save_prices(df):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(OUTPUT_PATH, orient="records", date_format="iso")


def main():
    print("🔄 Running Phase-2 Live Price Engine...")

    symbols = load_universe()
    prices = fetch_prices(symbols)
    save_prices(prices)

    print("✅ Live prices saved")
    print(f"📁 Output → {OUTPUT_PATH}")
    print(f"🕒 Timestamp → {datetime.utcnow().isoformat()} UTC")


if __name__ == "__main__":
    main()
