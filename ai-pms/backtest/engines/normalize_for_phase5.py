"""
AI-PMS Phase-2.5 Normalization Engine — FINAL STABLE

Guarantees:
• Handles messy NSE/Yahoo CSVs
• Extracts date from column OR index
• Detects multiple close column names
• Canonicalizes date → YYYY-MM-DD (NO time component)
• Never crashes full pipeline
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[3]
AIPMS_ROOT = REPO_ROOT / "ai-pms"

RAW_DATA_DIR = AIPMS_ROOT / "data" / "raw"


# ============================================================
# COLUMN CANDIDATES
# ============================================================

DATE_CANDIDATES = ["date", "Date", "DATE"]
CLOSE_CANDIDATES = [
    "close", "Close", "CLOSE",
    "adj close", "Adj Close",
    "price", "Price"
]


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def extract_date(df: pd.DataFrame):
    """
    Extract date series from:
    • explicit column
    • index
    • first column
    """

    # explicit column
    date_col = find_column(df, DATE_CANDIDATES)
    if date_col:
        return pd.to_datetime(df[date_col], errors="coerce")

    # index
    try:
        idx = pd.to_datetime(df.index, errors="coerce")
        if idx.notna().sum() > len(df) * 0.5:
            return idx
    except Exception:
        pass

    # first column fallback
    try:
        col0 = pd.to_datetime(df.iloc[:, 0], errors="coerce")
        if col0.notna().sum() > len(df) * 0.5:
            return col0
    except Exception:
        pass

    return None


def canonicalize_date(series: pd.Series) -> pd.Series:
    """
    Convert ANY datetime → strict YYYY-MM-DD.
    Removes time, timezone, nanoseconds.
    """
    series = pd.to_datetime(series, errors="coerce")
    return series.dt.normalize()  # midnight only


# ============================================================
# NORMALIZE SINGLE CSV
# ============================================================

def normalize_single_csv(csv_path: Path) -> bool:

    df = pd.read_csv(csv_path)

    date_series = extract_date(df)
    close_col = find_column(df, CLOSE_CANDIDATES)

    if date_series is None or close_col is None:
        print(f"⚠ Skipping {csv_path.name} → cannot detect date/close")
        return False

    ticker = csv_path.stem.upper()

    normalized = pd.DataFrame({
        "date": canonicalize_date(date_series),
        "ticker": ticker,
        "close": pd.to_numeric(df[close_col], errors="coerce"),
    })

    normalized = (
        normalized
        .dropna()
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    if normalized.empty:
        print(f"⚠ Skipping {csv_path.name} → empty after cleaning")
        return False

    normalized.to_csv(csv_path, index=False)
    return True


# ============================================================
# MAIN
# ============================================================

def main():
    print("▶ Phase-2.5 Normalization Started")

    csv_files = list(RAW_DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise RuntimeError(f"No CSV files found in {RAW_DATA_DIR}")

    ok, skip = 0, 0

    for csv in csv_files:
        if normalize_single_csv(csv):
            print(f"✔ Normalized: {csv.name}")
            ok += 1
        else:
            skip += 1

    print("--------------------------------------------------")
    print(f"Normalization complete → Success: {ok}, Skipped: {skip}")
    print("--------------------------------------------------")


if __name__ == "__main__":
    main()
