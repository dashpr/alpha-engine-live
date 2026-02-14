"""
PHASE-4 STEP-1
Historical Data Engine (GitHub production version)

Output:
    data/processed/prices_clean.parquet
"""

from __future__ import annotations
import pandas as pd
from pathlib import Path


RAW_DATA_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")
OUTPUT_FILE = PROCESSED_PATH / "prices_clean.parquet"

REQUIRED_COLUMNS = {"date", "symbol", "open", "high", "low", "close", "volume"}


class HistoricalDataEngine:
    """Clean and standardize historical equity price data."""

    def run(self) -> pd.DataFrame:
        df = self._load_all_files()
        df = self._standardize_schema(df)
        df = self._clean_duplicates(df)
        df = self._sort(df)
        df = self._ensure_continuous_dates(df)
        self._save(df)
        return df

    # ---------------- LOAD ----------------

    def _load_all_files(self) -> pd.DataFrame:
        if not RAW_DATA_PATH.exists():
            raise FileNotFoundError("data/raw folder not found")

        frames = []

        for file in RAW_DATA_PATH.glob("*"):
            if file.suffix.lower() == ".csv":
                frames.append(pd.read_csv(file))
            elif file.suffix.lower() in {".parquet", ".pq"}:
                frames.append(pd.read_parquet(file))

        if not frames:
            raise ValueError("No raw price files found in data/raw")

        return pd.concat(frames, ignore_index=True)

    # ---------------- CLEAN ----------------

    def _standardize_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df["symbol"] = df["symbol"].astype(str)

        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

        return df

    def _clean_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates(subset=["date", "symbol"])

    def _sort(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(["symbol", "date"]).reset_index(drop=True)

    def _ensure_continuous_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        out_frames = []

        for symbol, g in df.groupby("symbol"):
            g = g.set_index("date").sort_index()

            full_range = pd.date_range(g.index.min(), g.index.max(), freq="B")
            g = g.reindex(full_range)

            g["symbol"] = symbol
            g[["open", "high", "low", "close", "volume"]] = g[
                ["open", "high", "low", "close", "volume"]
            ].ffill()

            g = g.reset_index().rename(columns={"index": "date"})
            out_frames.append(g)

        return pd.concat(out_frames, ignore_index=True)

    # ---------------- SAVE ----------------

    def _save(self, df: pd.DataFrame) -> None:
        PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUTPUT_FILE, index=False)
        print(f"✓ prices_clean.parquet created → {OUTPUT_FILE}")


def main():
    engine = HistoricalDataEngine()
    df = engine.run()

    print("Rows:", len(df))
    print("Symbols:", df["symbol"].nunique())
    print("Date range:", df["date"].min(), "→", df["date"].max())


if __name__ == "__main__":
    main()
