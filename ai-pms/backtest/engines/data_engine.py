"""
Historical Data Engine — Phase-5 Institutional Backtest
Loads NSE historical dataset and prepares clean institutional dataframe.
"""

import os
from typing import List, Optional

import pandas as pd


RAW_DATA_PATH = "data/raw/nse_prices.csv"


class HistoricalDataEngine:
    def __init__(
        self,
        universe: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        universe : list[str] | str | None
            Symbols to include.
            • None → all symbols
            • str  → converted to single-item list

        start_date : str | None
            Filter start date (YYYY-MM-DD)

        end_date : str | None
            Filter end date (YYYY-MM-DD)
        """

        # --- normalize universe ---
        if isinstance(universe, str):
            universe = [universe]

        self.universe = universe
        self.start_date = pd.to_datetime(start_date) if start_date else None
        self.end_date = pd.to_datetime(end_date) if end_date else None

    # -----------------------------------------------------

    def _load_data(self) -> pd.DataFrame:
        """Load institutional NSE dataset."""

        if not os.path.exists(RAW_DATA_PATH):
            raise FileNotFoundError("data/raw/nse_prices.csv not found")

        df = pd.read_csv(
            RAW_DATA_PATH,
            parse_dates=["date"],
            low_memory=False,
        )

        return df

    # -----------------------------------------------------

    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply universe and date filters."""

        # --- universe filter ---
        if self.universe is not None:
            if not isinstance(self.universe, list):
                raise TypeError("Universe must be list of symbols")
            df = df[df["symbol"].isin(self.universe)]

        # --- start date ---
        if self.start_date is not None:
            df = df[df["date"] >= self.start_date]

        # --- end date ---
        if self.end_date is not None:
            df = df[df["date"] <= self.end_date]

        return df

    # -----------------------------------------------------

    def _final_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Final institutional cleaning."""

        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

        numeric_cols = ["open", "high", "low", "close", "adj_close", "volume"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["close"])

        return df

    # -----------------------------------------------------

    def run(self) -> pd.DataFrame:
        """Main execution."""

        df = self._load_data()
        df = self._apply_filters(df)
        df = self._final_clean(df)

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique()}")
        print(
            f"Date span: {df['date'].min().date()} → {df['date'].max().date()}"
        )

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
