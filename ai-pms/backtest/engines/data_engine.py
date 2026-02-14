import os
import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Institutional historical data loader.
    Auto-detects project root so it works in:
    - Local machine
    - GitHub Actions
    - Docker / cloud
    """

    def __init__(self, data_folder: str | None = None):
        """
        If data_folder is None → auto-resolve:
        project_root / data / raw
        """

        if data_folder is not None:
            self.data_folder = Path(data_folder)
        else:
            # Detect project root dynamically
            current = Path(__file__).resolve()

            # backtest/engines/data_engine.py → ai-pms/
            project_root = current.parents[2]

            self.data_folder = project_root / "data" / "raw"

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

            # ---- normalize column names ----
            df.columns = [c.lower().strip() for c in df.columns]

            required = {"date", "open", "high", "low", "close", "volume"}
            if not required.issubset(df.columns):
                raise ValueError(f"{file} missing required columns")

            df["symbol"] = file.replace(".csv", "")
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

            df = df.dropna(subset=["date"])

            frames.append(
                df[["date", "symbol", "open", "high", "low", "close", "volume"]]
            )

        if not frames:
            raise ValueError("No CSV files found in raw data folder")

        return pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    def _compute_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(["symbol", "date"])

        # next-day executable return
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
