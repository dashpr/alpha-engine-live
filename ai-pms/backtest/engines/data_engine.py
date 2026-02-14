import os
import pandas as pd


class HistoricalDataEngine:
    """
    Institutional-grade historical CSV loader
    Handles:
    - Multiple CSV files
    - Column normalization
    - Schema validation
    """

    def __init__(self, data_folder: str = "data/raw"):
        self.data_folder = data_folder

    # -------------------------------------------------------
    # Public runner
    # -------------------------------------------------------
    def run(self) -> pd.DataFrame:
        if not os.path.exists(self.data_folder):
            raise FileNotFoundError(f"{self.data_folder} not found")

        print("📊 Loading historical data...")

        df = self._load_csvs()
        df = self._clean_schema(df)

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique():,}")
        print(f"Date span: {df['date'].min()} → {df['date'].max()}")

        return df

    # -------------------------------------------------------
    # Load all CSV files
    # -------------------------------------------------------
    def _load_csvs(self) -> pd.DataFrame:
        frames = []

        for file in os.listdir(self.data_folder):
            if not file.endswith(".csv"):
                continue

            path = os.path.join(self.data_folder, file)
            df = pd.read_csv(path)

            frames.append(df)

        if not frames:
            raise ValueError("No CSV files found in data folder")

        return pd.concat(frames, ignore_index=True)

    # -------------------------------------------------------
    # Clean + normalize schema
    # -------------------------------------------------------
    def _clean_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        # Normalize column names
        df.columns = [c.strip().lower() for c in df.columns]

        # Map common variations → canonical names
        column_map = {
            "date": "date",
            "timestamp": "date",

            "close": "close",
            "adj close": "close",

            "open": "open",
            "high": "high",
            "low": "low",
            "volume": "volume",

            "ticker": "symbol",
            "symbol": "symbol",
        }

        df = df.rename(columns=column_map)

        # Required columns
        required = {"date", "close", "symbol"}
        missing = required - set(df.columns)

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Convert types
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        # Drop bad rows
        df = df.dropna(subset=["date", "close", "symbol"])

        # Sort properly
        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

        return df
