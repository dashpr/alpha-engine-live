# ai-pms/backtest/engines/data_engine.py

import os
import pandas as pd


class HistoricalDataEngine:
    def __init__(self, data_folder: str):
        self.data_folder = data_folder

    def _load_csvs(self) -> pd.DataFrame:
        if not os.path.exists(self.data_folder):
            raise FileNotFoundError(f"{self.data_folder} not found")

        all_files = [
            os.path.join(self.data_folder, f)
            for f in os.listdir(self.data_folder)
            if f.endswith(".csv")
        ]

        dfs = []

        for file in all_files:
            df = pd.read_csv(file)

            # normalize columns
            df.columns = [c.lower() for c in df.columns]

            df = df.rename(
                columns={
                    "date": "date",
                    "close": "close",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "volume": "volume",
                    "ticker": "symbol",
                }
            )

            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date", "close", "symbol"])

            dfs.append(df[["date", "symbol", "open", "high", "low", "close", "volume"]])

        return pd.concat(dfs).sort_values(["date", "symbol"])

    def run(self) -> pd.DataFrame:
        return self._load_csvs()
