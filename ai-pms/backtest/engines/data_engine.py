"""
Historical Data Engine
Loads Nifty-300 CSV history for institutional backtesting
"""

import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Production-grade historical loader
    """

    def __init__(self, data_folder: str = "data/raw/nifty300"):
        self.data_folder = Path(data_folder)

    # ======================================================
    # MAIN ENTRY
    # ======================================================

    def run(self) -> pd.DataFrame:
        if not self.data_folder.exists():
            raise FileNotFoundError(f"{self.data_folder} not found")

        df = self._load_all_csv()
        df = self._clean_dataframe(df)

        return df

    # ======================================================
    # LOAD ALL CSV FILES
    # ======================================================

    def _load_all_csv(self) -> pd.DataFrame:
        files = list(self.data_folder.glob("*.csv"))

        if not files:
            raise FileNotFoundError(f"No CSV files inside {self.data_folder}")

        all_data = []

        for f in files:
            try:
                temp = pd.read_csv(f)

                # infer symbol from filename
                symbol = f.stem.upper()
                temp["symbol"] = symbol

                all_data.append(temp)

            except Exception as e:
                print(f"⚠️ Skipped {f.name} → {e}")

        if not all_data:
            raise ValueError("No valid CSV data loaded")

        return pd.concat(all_data, ignore_index=True)

    # ======================================================
    # CLEAN DATAFRAME
    # ======================================================

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        # --- standard column rename (case-safe)
        df.columns = [c.lower().strip() for c in df.columns]

        # --- required columns
        required = {"date", "open", "high", "low", "close", "volume", "symbol"}
        missing = required - set(df.columns)

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # --- date parsing (fast & safe)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # --- numeric conversion
        price_cols = ["open", "high", "low", "close", "volume"]

        for col in price_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # --- drop bad rows
        df = df.dropna(subset=["date", "close"])

        # --- sort for backtest engines
        df = df.sort_values(["date", "symbol"]).reset_index(drop=True)

        return df
