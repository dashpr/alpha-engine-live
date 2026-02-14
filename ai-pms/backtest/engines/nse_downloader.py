"""
NSE Historical Data Downloader
Phase-5 Institutional Backtest Data Source

Downloads daily OHLCV for NIFTY Top-200 universe using yfinance
and saves clean institutional dataset for backtesting.
"""

import os
from datetime import datetime
from typing import List

import pandas as pd
import yfinance as yf


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

START_DATE = "2010-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")

RAW_DATA_DIR = "data/raw"
OUTPUT_CSV = os.path.join(RAW_DATA_DIR, "nse_prices.csv")
OUTPUT_PARQUET = os.path.join(RAW_DATA_DIR, "nse_prices.parquet")


# NIFTY TOP-200 placeholder universe (can upgrade later)
NSE_SYMBOLS: List[str] = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "HINDUNILVR.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "LT.NS",
]


# ---------------------------------------------------------
# DOWNLOAD ENGINE
# ---------------------------------------------------------


class NSEDownloader:
    def __init__(
        self,
        symbols: List[str] = NSE_SYMBOLS,
        start: str = START_DATE,
        end: str = END_DATE,
    ):
        self.symbols = symbols
        self.start = start
        self.end = end

        os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # -----------------------------------------------------

    def download_symbol(self, symbol: str) -> pd.DataFrame:
        """
        Download single symbol OHLCV.
        """
        df = yf.download(
            symbol,
            start=self.start,
            end=self.end,
            progress=False,
            auto_adjust=False,
        )

        if df.empty:
            return pd.DataFrame()

        df = df.reset_index()
        df["symbol"] = symbol

        return df

    # -----------------------------------------------------

    def run(self) -> pd.DataFrame:
        """
        Download full universe and save institutional dataset.
        """
        all_data = []

        for sym in self.symbols:
            print(f"Downloading {sym} ...")
            df = self.download_symbol(sym)

            if not df.empty:
                all_data.append(df)

        if not all_data:
            raise ValueError("No data downloaded from NSE.")

        final_df = pd.concat(all_data, ignore_index=True)

        # -----------------------------
        # Standard column format
        # -----------------------------
        final_df = final_df.rename(
            columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )

        final_df = final_df.sort_values(["symbol", "date"])

        # -----------------------------
        # Save outputs
        # -----------------------------
        final_df.to_csv(OUTPUT_CSV, index=False)
        final_df.to_parquet(OUTPUT_PARQUET, index=False)

        print(f"\nSaved CSV → {OUTPUT_CSV}")
        print(f"Saved Parquet → {OUTPUT_PARQUET}")

        return final_df


# ---------------------------------------------------------
# CLI ENTRY
# ---------------------------------------------------------

def main():
    print("\n🚀 Running NSE Historical Downloader (2010–Present)\n")

    downloader = NSEDownloader()
    downloader.run()

    print("\n✅ NSE download complete.\n")


if __name__ == "__main__":
    main()
