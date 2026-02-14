"""
Historical Data Engine — Phase-5 Institutional Backtest
Loads NSE historical dataset and prepares clean institutional dataframe.
"""

import os
from typing import List, Optional

import pandas as pd


RAW_DATA_PATH = "data/raw/nse_prices.csv"


class HistoricalDataEngine:
    def __init__(self, universe: Optional[List[str]] = None):
        """
        universe:
            • None  → use all symbols in dataset
            • list → filter to provided symbols
            • str  → auto convert to single-item list
        """

        # ---- normalize universe input ----
        if isinstance(universe, str):
            universe = [universe]

        self.universe = universe

    # -----------------------------------------------------

    def _load_all_files(self) -> pd.DataFrame:
        """Load institutional NSE dataset."""

        if not os.path.exists(RAW_DATA_PATH):
            raise FileNotFoundError("data/raw/nse_prices.csv not found")

        df = pd.read_csv(
            RAW_DATA_PATH,
            parse_dates=["date"],
            low_memory=False,  # fixes dtype warning
        )

        return df

    # -----------------------------------------------------

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply universe filtering if provided."""

        if self.universe is None:
            return df

        if not isinstance(self.universe, list):
            raise TypeError("Universe must be list of symbols")

        df = df[df["symbol"].isin(self.universe)]

        return df

    # -----------------------------------------------------

    def _final_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final institutional cleaning."""

        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

        # ensure numeric
        numeric_cols = ["open", "high", "low", "close", "adj_close", "volume"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["close"])

        return df

    # -----------------------------------------------------

    def run(self) -> pd.DataFrame:
        """Main execution."""

        df = self._load_all_files()
        df = self._apply_filters(df)
        df = self._final_clean(df)

        print(f"\nLoaded rows: {len(df):,}")
        print(f"Symbols: {df['symbol'].nunique()}")

        return df


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

def main():
    print("\n🚀 Running Historical Data Engine\n")

    engine = HistoricalDataEngine()
    df = engine.run()

    print("\n✅ Data ready for Phase-5 backtest\n")
    print(df.head())


if __name__ == "__main__":
    main()
