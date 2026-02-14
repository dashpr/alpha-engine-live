"""
REAL NSE Historical Loader — Institutional Grade
Supports partial universe (e.g., 240 of NIFTY 300)

Builds permanent parquet spine for Phase-5 backtests.
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


# ------------------------------------------------------------
# Column standardization
# ------------------------------------------------------------
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
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


# ------------------------------------------------------------
# Load one CSV
# ------------------------------------------------------------
def load_single_csv(path: Path) -> pd.DataFrame:
    symbol = path.stem.upper()

    df = pd.read_csv(path, low_memory=False)

    df = standardize_columns(df)

    df["symbol"] = symbol

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.dropna(subset=["date", "close"])

    return df


# ------------------------------------------------------------
# Load all CSVs
# ------------------------------------------------------------
def load_all_data() -> pd.DataFrame:
    if not RAW_DIR.exists():
        raise FileNotFoundError("❌ data/raw folder not found")

    files = sorted(RAW_DIR.glob("*.csv"))

    if not files:
        raise FileNotFoundError("❌ No CSV files found in data/raw")

    print(f"📂 Found {len(files)} stock files\n")

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


# ------------------------------------------------------------
# Institutional sanity checks
# ------------------------------------------------------------
def validate_dataset(df: pd.DataFrame):
    rows = len(df)
    symbols = df["symbol"].nunique()
    start = df["date"].min()
    end = df["date"].max()

    print("📊 DATA VALIDATION")
    print(f"Rows     : {rows:,}")
    print(f"Symbols  : {symbols}")
    print(f"Date span: {start.date()} → {end.date()}\n")

    if symbols < 150:
        raise ValueError("❌ Too few symbols for institutional backtest")

    if start.year > 2012:
        raise ValueError("❌ History too short (<2012)")

    if rows < 500_000:
        raise ValueError("❌ Dataset too small for reliable CAGR")


# ------------------------------------------------------------
# Save parquet spine
# ------------------------------------------------------------
def save_parquet(df: pd.DataFrame):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df.to_parquet(OUTPUT_FILE, index=False)

    print(f"✅ Saved institutional dataset → {OUTPUT_FILE}\n")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print("🚀 Building REAL NSE Institutional Dataset...\n")

    df = load_all_data()

    validate_dataset(df)

    save_parquet(df)


if __name__ == "__main__":
    main()
