import pandas as pd
from pathlib import Path


class HistoricalDataEngine:
    """
    Loads historical CSV files from:
    ai-pms/data/raw/

    Each CSV must contain:
    date, open, high, low, close, volume
    """

    def __init__(self, data_folder: str = "data/raw"):
        self.data_folder = Path(data_folder)

    # =====================================================
    def _load_single_file(self, file_path: Path):
        df = pd.read_csv(file_path)

        # ---- Standardise column names
        df.columns = [c.lower().strip() for c in df.columns]

        # ---- Required columns
        required = {"date", "open", "high", "low", "close", "volume"}
        if not required.issubset(set(df.columns)):
            return None

        # ---- Parse date safely
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # ---- Convert numeric columns
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["date", "close"])

        # ---- Add symbol from filename
        df["symbol"] = file_path.stem.upper()

        return df[["date", "symbol", "open", "high", "low", "close", "volume"]]

    # =====================================================
    def run(self):
        if not self.data_folder.exists():
            raise FileNotFoundError(f"{self.data_folder} not found")

        files = list(self.data_folder.glob("*.csv"))

        if len(files) == 0:
            raise FileNotFoundError("No CSV files found in data/raw")

        dfs = []

        for f in files:
            df = self._load_single_file(f)
            if df is not None:
                dfs.append(df)

        if len(dfs) == 0:
            raise ValueError("No valid price data loaded")

        full_df = pd.concat(dfs, ignore_index=True)
        full_df = full_df.sort_values(["date", "symbol"])

        return full_df
