import os
import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Institutional historical data loader.

    Robust to:
    - Multiple NSE CSV schemas
    - Column naming inconsistencies
    - Future unknown formats
    """

    # -----------------------------------------------------
    def __init__(self, data_folder: str | None = None):

        if data_folder:
            self.data_folder = Path(data_folder)
        else:
            current = Path(__file__).resolve()
            project_root = current.parents[2]
            self.data_folder = project_root / "data" / "raw"

    # -----------------------------------------------------
    def _detect_columns(self, df: pd.DataFrame, file: str) -> pd.DataFrame:
        """
        Intelligent column detection instead of hardcoded mapping.
        """

        cols = {c.lower().strip(): c for c in df.columns}
        lower_cols = list(cols.keys())

        # -------- DATE --------
        date_col = None
        for c in lower_cols:
            if "date" in c:
                date_col = cols[c]
                break
        if not date_col:
            raise ValueError(f"{file} → date column not found")

        # -------- PRICE / CLOSE --------
        close_col = None
        for key in ["close", "adj close", "price"]:
            if key in lower_cols:
                close_col = cols[key]
                break
        if not close_col:
            raise ValueError(f"{file} → close/price column not found")

        # -------- OPEN / HIGH / LOW / VOLUME --------
        def find(name):
            for c in lower_cols:
                if name in c:
                    return cols[c]
            return None

        open_col = find("open")
        high_col = find("high")
        low_col = find("low")
        vol_col = find("vol")

        required = [open_col, high_col, low_col, vol_col]
        if any(c is None for c in required):
            raise ValueError(f"{file} → missing OHLCV columns → {df.columns.tolist()}")

        # -------- STANDARDIZE --------
        df = df.rename(
            columns={
                date_col: "date",
                open_col: "open",
                high_col: "high",
                low_col: "low",
                close_col: "close",
                vol_col: "volume",
            }
        )

        return df[["date", "open", "high", "low", "close", "volume"]]

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

            # ---- intelligent normalization ----
            df = self._detect_columns(df, file)

            # ---- parse date ----
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            # ---- symbol ----
            df["symbol"] = file.replace(".csv", "")

            frames.append(df)

        if not frames:
            raise ValueError("No valid CSV files found in raw data folder")

        return pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    def _compute_returns(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.sort_values(["symbol", "date"])

        # Executable next-day open return (institutional reality)
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
