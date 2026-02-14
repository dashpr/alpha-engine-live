import os
import pandas as pd
from typing import List


class HistoricalDataEngine:
    """
    Institutional Historical Data Loader
    Reads ALL CSVs from data/raw, cleans numerics, merges to single dataframe.
    """

    def __init__(self, data_path: str = "data/raw"):
        self.data_path = data_path

    # -----------------------------------------------------
    # Clean numeric columns safely
    # -----------------------------------------------------
    def _clean_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = ["open", "high", "low", "close", "volume"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace(" ", "", regex=False)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    # -----------------------------------------------------
    # Load all symbol CSVs
    # -----------------------------------------------------
    def _load_data(self) -> pd.DataFrame:
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"{self.data_path} folder not found")

        files: List[str] = [f for f in os.listdir(self.data_path) if f.endswith(".csv")]

        if len(files) == 0:
            raise FileNotFoundError("No CSV files found in data/raw")

        dfs = []

        for file in files:
            symbol = file.replace(".csv", "").upper()
            path = os.path.join(self.data_path, file)

            df = pd.read_csv(path)

            # --- Standardize column names ---
            df.columns = [c.lower().strip() for c in df.columns]

            # --- Fix date column ---
            if "date" not in df.columns:
                df.rename(columns={df.columns[0]: "date"}, inplace=True)

            df["date"] = pd.to_datetime(df["date"], errors="coerce")

            # --- Clean numerics ---
            df = self._clean_numeric(df)

            # --- Keep required columns ---
            keep_cols = [c for c in ["date", "open", "high", "low", "close", "volume"] if c in df.columns]
            df = df[keep_cols].copy()

            df["symbol"] = symbol

            dfs.append(df)

        merged = pd.concat(dfs, ignore_index=True)

        # Drop rows without close price
        merged = merged.dropna(subset=["close"])

        return merged

    # -----------------------------------------------------
    # Public run method
    # -----------------------------------------------------
    def run(self) -> pd.DataFrame:
        df = self._load_data()

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique()}")
        print(f"Date span: {df['date'].min()} → {df['date'].max()}")

        return df
