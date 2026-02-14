import os
import pandas as pd


class HistoricalDataEngine:
    """
    Institutional historical data loader.
    Reads all CSVs from ai-pms/data/raw and produces a clean panel dataframe.
    """

    def __init__(self, data_folder="ai-pms/data/raw"):
        self.data_folder = data_folder

    # -----------------------------------------------------
    def _load_csvs(self) -> pd.DataFrame:
        if not os.path.exists(self.data_folder):
            raise FileNotFoundError(f"{self.data_folder} not found")

        frames = []

        for file in os.listdir(self.data_folder):
            if not file.endswith(".csv"):
                continue

            path = os.path.join(self.data_folder, file)
            df = pd.read_csv(path)

            # ---- Standard column mapping ----
            df.columns = [c.lower() for c in df.columns]

            required = {"date", "open", "high", "low", "close", "volume"}
            if not required.issubset(set(df.columns)):
                raise ValueError(f"{file} missing required columns")

            ticker = file.replace(".csv", "")
            df["symbol"] = ticker

            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            frames.append(df[["date", "symbol", "open", "high", "low", "close", "volume"]])

        if not frames:
            raise ValueError("No CSV files found in raw data folder")

        return pd.concat(frames, ignore_index=True)

    # -----------------------------------------------------
    def _compute_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(["symbol", "date"])

        # next-day open return (execution realistic)
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

        df = self._load_csvs()
        df = self._compute_returns(df)

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique()}")
        print(f"Date span: {df['date'].min()} → {df['date'].max()}")

        return df
