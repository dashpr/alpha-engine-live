import os
import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Institutional historical data loader.

    Handles:
    - Different NSE CSV schemas
    - Local + GitHub + cloud paths
    - Automatic normalization
    """

    def __init__(self, data_folder: str | None = None):

        if data_folder:
            self.data_folder = Path(data_folder)
        else:
            current = Path(__file__).resolve()
            project_root = current.parents[2]
            self.data_folder = project_root / "data" / "raw"

    # -----------------------------------------------------
    def _standardize_columns(self, df: pd.DataFrame, file: str) -> pd.DataFrame:
        """
        Convert different NSE column formats → internal schema
        """

        df.columns = [c.lower().strip() for c in df.columns]

        # Possible mappings
        column_map_options = [
            # Standard OHLCV
            {"date": "date", "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"},
            # Your NSE export format
            {"date": "date", "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"},
            # Alternate: capitalized
            {"date": "date", "open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"},
            # Format: Date Close High Low Open Volume
            {"date": "date", "close": "close", "high": "high", "low": "low", "open": "open", "volume": "volume"},
        ]

        for mapping in column_map_options:
            if set(mapping.keys()).issubset(df.columns):
                df = df.rename(columns=mapping)
                return df

        raise ValueError(f"{file} has unsupported column structure → {df.columns.tolist()}")

    # -----------------------------------------------------
    def _load_csvs(self) -> pd.DataFrame:

        if not self.data_folder.exists():
            raise FileNotFoundError(f"{self.data_folder} not found")

        frames = []

        for file in os.listdir(self.data_folder):

            if not file.endswith(".csv"):
                continue

            path = self.data_folder / file
            df = pd.read_csv(path)

            # ---- normalize schema ----
            df = self._standardize_columns(df, file)

            # ---- parse date ----
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            df["symbol"] = file.replace(".csv", "")

            frames.append(
                df[["date", "symbol", "open", "high", "low", "close", "volume"]]
            )

        if not frames:
            raise ValueError("No valid CSV files found in raw data folder")

        return pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    def _compute_returns(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.sort_values(["symbol", "date"])

        # Executable next-day open return
        df["ret_1d"] = (
            df.groupby("symbol")["open"]
            .shift(-1)
            .div(df["open"])
            .sub(1)
        )

        return df.dropna(subset=["ret_1d"])

    # -----------------------------------------------------
    def run(self) -> pd.DataFrame:

        print("📊 Loading historical data...")
        print(f"📂 Using data folder → {self.data_folder}")

        df = self._load_csvs()
        df = self._compute_returns(df)

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique()}")
        print(f"Date span: {df['date'].min()} → {df['date'].max()}")

        return df
