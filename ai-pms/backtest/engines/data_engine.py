"""
Institutional Historical Data Engine
------------------------------------

Loads raw NSE CSV files from:

    ai-pms/data/raw/

and converts them into a clean institutional dataframe:

    columns → date, symbol, open, high, low, close, volume

Robust against:
- Different column names
- Missing headers
- Timestamp/date variations
- Mixed NSE export formats
"""

from pathlib import Path
import pandas as pd


class HistoricalDataEngine:
    """
    Institutional-grade historical data loader.
    """

    def __init__(self, data_folder: str | None = None):
        base = Path(__file__).resolve().parents[2]  # ai-pms root

        self.data_folder = (
            Path(data_folder)
            if data_folder
            else base / "data" / "raw"
        )

    # ------------------------------------------------------------------
    # PUBLIC RUN
    # ------------------------------------------------------------------
    def run(self) -> pd.DataFrame:
        print("📊 Loading historical data...")

        if not self.data_folder.exists():
            raise FileNotFoundError(f"{self.data_folder} not found")

        print(f"📂 Using data folder → {self.data_folder}")

        df = self._load_csvs()

        print("\n📊 Historical Data Loaded")
        print(f"Rows     : {len(df):,}")
        print(f"Symbols  : {df['symbol'].nunique()}")
        print(f"Date span: {df['date'].min()} → {df['date'].max()}")

        return df

    # ------------------------------------------------------------------
    # LOAD ALL CSVs
    # ------------------------------------------------------------------
    def _load_csvs(self) -> pd.DataFrame:
        frames = []

        for file in sorted(self.data_folder.glob("*.csv")):
            try:
                df = pd.read_csv(file)
                df = self._detect_columns(df, file.name)

                df["symbol"] = file.stem.upper()
                frames.append(df)

            except Exception as e:
                print(f"⚠️ Skipping {file.name} → {e}")

        if not frames:
            raise ValueError("No valid CSV files found in data/raw")

        df = pd.concat(frames, ignore_index=True)

        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

        return df

    # ------------------------------------------------------------------
    # SMART COLUMN DETECTION (INSTITUTIONAL GRADE)
    # ------------------------------------------------------------------
    def _detect_columns(self, df: pd.DataFrame, file: str) -> pd.DataFrame:
        """
        Detect DATE by datatype, not only name.
        """

        cols = list(df.columns)
        lower = [c.lower().strip() for c in cols]

        # --------------------------------------------------
        # 1️⃣ Name-based date detection
        # --------------------------------------------------
        date_col = None
        for c in cols:
            if "date" in c.lower() or "time" in c.lower():
                date_col = c
                break

        # --------------------------------------------------
        # 2️⃣ Datatype-based detection if needed
        # --------------------------------------------------
        if date_col is None:
            for c in cols:
                parsed = pd.to_datetime(df[c], errors="coerce")
                if parsed.notna().mean() > 0.8:
                    date_col = c
                    df[c] = parsed
                    break

        if date_col is None:
            raise ValueError(f"{file} → date column not detectable")

        # --------------------------------------------------
        # CLOSE / PRICE detection
        # --------------------------------------------------
        close_col = None
        for key in ["close", "adj close", "price"]:
            for c in cols:
                if key in c.lower():
                    close_col = c
                    break
            if close_col:
                break

        if close_col is None:
            raise ValueError(f"{file} → close/price column not found")

        # --------------------------------------------------
        # OHLCV detection helpers
        # --------------------------------------------------
        def find(name: str):
            for c in cols:
                if name in c.lower():
                    return c
            return None

        open_col = find("open")
        high_col = find("high")
        low_col = find("low")
        vol_col = find("vol")

        if any(c is None for c in [open_col, high_col, low_col, vol_col]):
            raise ValueError(
                f"{file} → missing OHLCV columns → {df.columns.tolist()}"
            )

        # --------------------------------------------------
        # STANDARDIZE
        # --------------------------------------------------
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

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # ensure numeric
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["date", "close"])

        return df[["date", "open", "high", "low", "close", "volume"]]
