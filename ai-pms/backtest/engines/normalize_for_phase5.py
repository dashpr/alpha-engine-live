"""
AI-PMS Phase-2.5 Normalization Engine — FINAL (Production Grade)

Handles:
• Date in column OR index
• Multiple Close column names
• Real-world messy NSE/Yahoo CSVs
• Never crashes full pipeline — skips bad files safely
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
    "adj close", "Adj Close", "ADJ CLOSE",
    "price", "Price", "PRICE"
]


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def extract_date_series(df: pd.DataFrame):
    """
    Return a pandas Series of dates from:
    • explicit date column
    • index if datetime-like
    • first unnamed column
    """

    # Case-1: explicit column
    date_col = find_column(df, DATE_CANDIDATES)
    if date_col:
        return pd.to_datetime(df[date_col], errors="coerce")

    # Case-2: index contains dates
    try:
        idx_dates = pd.to_datetime(df.index, errors="coerce")
        if idx_dates.notna().sum() > len(df) * 0.5:
            return idx_dates
    except Exception:
        pass

    # Case-3: first unnamed column
    first_col = df.columns[0]
    try:
        col_dates = pd.to_datetime(df[first_col], errors="coerce")
        if col_dates.notna().sum() > len(df) * 0.5:
            return col_dates
    except Exception:
        pass

    return None


# ============================================================
# NORMALIZE SINGLE CSV
# ============================================================

def normalize_single_csv(csv_path: Path) -> bool:
    """
    Returns True if normalized successfully, False if skipped.
    """

    df = pd.read_csv(csv_path)

    # ----- detect date -----
    date_series = extract_date_series(df)

    # ----- detect close -----
    close_col = find_column(df, CLOSE_CANDIDATES)

    if date_series is None or close_col is None:
        print(
            f"⚠ Skipping {csv_path.name} "
            f"(date or close not detectable). "
            f"Columns: {list(df.columns)}"
        )
        return False

    ticker = csv_path.stem.upper()

    normalized = pd.DataFrame({
        "date": date_series,
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
        print(f"⚠ Skipping {csv_path.name} (empty after cleaning)")
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

    success = 0
    skipped = 0

    for csv_path in csv_files:
        if normalize_single_csv(csv_path):
            print(f"✔ Normalized: {csv_path.name}")
            success += 1
        else:
            skipped += 1

    print("--------------------------------------------------")
    print(f"Normalization complete → Success: {success}, Skipped: {skipped}")
    print("--------------------------------------------------")


if __name__ == "__main__":
    main()
