"""
REAL NSE Historical Loader — Institutional Grade
Handles: One CSV per stock (Option A)

Output:
    data/processed/nse_2010_2024.parquet
"""

from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "nse_2010_2024.parquet"


REQUIRED_COLUMNS = {
    "date": ["date", "Date", "DATE"],
    "open": ["open", "Open", "OPEN"],
    "high": ["high", "High", "HIGH"],
    "low": ["low", "Low", "LOW"],
    "close": ["close", "Close", "CLOSE", "adj close", "Adj Close"],
    "volume": ["volume", "Volume", "VOLUME"],
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map various column name styles to standard schema."""
    col_map = {}

    for std_col, variants in REQUIRED_COLUMNS.items():
        for v in variants:
            if v in df.columns:
                col_map[v] = std_col
                break

    df = df.rename(columns=col_map)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df[["date", "open", "high", "low", "close", "volume"]]


def load_single_csv(path: Path) -> pd.DataFrame:
    """Load one stock CSV and attach symbol."""
    symbol = path.stem.upper()

    df = pd.read_csv(path)

    df = standardize_columns(df)

    df["symbol"] = symbol

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date", "close"])

    return df


def load_all_data() -> pd.DataFrame:
    """Load and combine all stock CSVs."""
    if not RAW_DIR.exists():
        raise FileNotFoundError("❌ data/raw folder not found")

    files = sorted(RAW_DIR.glob("*.csv"))

    if not files:
        raise FileNotFoundError("❌ No CSV files found in data/raw")

    print(f"📂 Found {len(files)} stock files")

    dfs = []

    for f in files:
        try:
            dfs.append(load_single_csv(f))
        except Exception as e:
            print(f"⚠️ Skipping {f.name}: {e}")

    if not dfs:
        raise ValueError("❌ No valid stock data loaded")

    df = pd.concat(dfs, ignore_index=True)

    df = df.sort_values(["symbol", "date"])

    return df


def save_parquet(df: pd.DataFrame):
    """Save processed institutional dataset."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_parquet(OUTPUT_FILE, index=False)

    print("\n✅ REAL NSE DATA READY")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique()}")
    print(f"Date span: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"Saved to : {OUTPUT_FILE}\n")


def main():
    print("🚀 Building REAL NSE Institutional Dataset...\n")

    df = load_all_data()

    save_parquet(df)


if __name__ == "__main__":
    main()
