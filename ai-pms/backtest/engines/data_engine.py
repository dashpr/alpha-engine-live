import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Institutional Historical Data Engine
    -----------------------------------
    Loads and prepares historical price data for backtesting.
    """

    def __init__(
        self,
        raw_data_path: str = "data/raw",
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        self.raw_path = Path(raw_data_path)
        self.start_date = start_date
        self.end_date = end_date

    # --------------------------------------------------
    # Public Runner
    # --------------------------------------------------
    def run(self) -> pd.DataFrame:
        df = self._load_all_files()
        df = self._apply_date_filter(df)
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

        # Ensure required columns
        required_cols = {"date", "symbol", "close"}
        if not required_cols.issubset(df.columns):
            raise ValueError("Raw data must contain: date, symbol, close")

        df["date"] = pd.to_datetime(df["date"])

        return df

    # --------------------------------------------------
    # Date filtering
    # --------------------------------------------------
    def _apply_date_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.start_date:
            df = df[df["date"] >= pd.to_datetime(self.start_date)]

        if self.end_date:
            df = df[df["date"] <= pd.to_datetime(self.end_date)]

        return df
