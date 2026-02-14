import pandas as pd
from pathlib import Path
from typing import list, Optional


class HistoricalDataEngine:
    """
    Institutional Historical Data Engine
    -----------------------------------
    Loads and prepares historical price data for backtesting.
    Supports:
        • universe filtering
        • date filtering
        • scalable raw data ingestion
    """

    def __init__(
        self,
        raw_data_path: str = "data/raw",
        universe: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        self.raw_path = Path(raw_data_path)
        self.universe = universe
        self.start_date = start_date
        self.end_date = end_date

    # --------------------------------------------------
    # Public runner
    # --------------------------------------------------
    def run(self) -> pd.DataFrame:
        df = self._load_all_files()
        df = self._apply_filters(df)
        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
        return df

    # --------------------------------------------------
    # Load raw CSV/parquet files
    # --------------------------------------------------
    def _load_all_files(self) -> pd.DataFrame:
        if not self.raw_path.exists():
            raise FileNotFoundError("data/raw folder not found")

        files = list(self.raw_path.glob("*.csv")) + list(self.raw_path.glob("*.parquet"))

        if not files:
            raise FileNotFoundError("No raw data files found in data/raw")

        dfs = []

        for f in files:
            if f.suffix == ".csv":
                df = pd.read_csv(f)
            else:
                df = pd.read_parquet(f)

            dfs.append(df)

        df = pd.concat(dfs, ignore_index=True)

        required_cols = {"date", "symbol", "close"}
        if not required_cols.issubset(df.columns):
            raise ValueError("Raw data must contain: date, symbol, close")

        df["date"] = pd.to_datetime(df["date"])

        return df

    # --------------------------------------------------
    # Apply universe + date filters
    # --------------------------------------------------
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.universe:
            df = df[df["symbol"].isin(self.universe)]

        if self.start_date:
            df = df[df["date"] >= pd.to_datetime(self.start_date)]

        if self.end_date:
            df = df[df["date"] <= pd.to_datetime(self.end_date)]

        return df
