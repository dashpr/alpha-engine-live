"""
AI-PMS Phase-2.5 Normalization Engine (FINAL HARDENED)

Purpose:
Convert heterogeneous NSE/Yahoo OHLCV CSV formats into
Phase-5 institutional schema:

    date,ticker,close

Design:
- Deterministic
- Fail-safe validation
- Handles real-world column name variations
- CI compatible
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[3]
AIPMS_ROOT = REPO_ROOT / "ai-pms"

RAW_DATA_DIR = AIPMS_ROOT / "data" / "raw"


# ============================================================
# COLUMN NORMALIZATION MAP
# ============================================================

DATE_CANDIDATES = [
    "date", "Date", "DATE"
]

CLOSE_CANDIDATES = [
    "close", "Close", "CLOSE",
    "adj close", "Adj Close", "ADJ CLOSE",
    "close price", "Close Price"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(df, candidates):
    """Return first matching column name from candidates."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


# ============================================================
# NORMALIZE SINGLE CSV
# ============================================================

def normalize_single_csv(csv_path: Path) -> None:

    df = pd.read_csv(csv_path)

    # --------------------------------------------------------
    # Detect required columns robustly
    # --------------------------------------------------------
    date_col = find_column(df, DATE_CANDIDATES)
    close_col = find_column(df, CLOSE_CANDIDATES)

    if date_col is None or close_col is None:
        raise RuntimeError(
            f"❌ Cannot normalize {csv_path.name} → "
            f"missing recognizable Date/Close columns.\n"
            f"Available columns: {list(df.columns)}"
        )

    ticker = csv_path.stem.upper()

    normalized = pd.DataFrame({
        "date": pd.to_datetime(df[date_col], errors="coerce"),
        "ticker": ticker,
        "close": pd.to_numeric(df[close_col], errors="coerce"),
    })

    # --------------------------------------------------------
    # Deterministic cleaning
    # --------------------------------------------------------
    normalized = (
        normalized
        .dropna()
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    if normalized.empty:
        raise RuntimeError(f"❌ {csv_path.name} produced empty normalized data")

    # --------------------------------------------------------
    # Overwrite original CSV
    # --------------------------------------------------------
    normalized.to_csv(csv_path, index=False)


# ============================================================
# MAIN RUNNER
# ============================================================

def main():
    print("▶ Phase-2.5 Normalization Started")

    csv_files = list(RAW_DATA_DIR.glob("*.csv"))

    if not csv_files:
        raise RuntimeError(f"❌ No CSV files found in {RAW_DATA_DIR}")

    for csv_path in csv_files:
        normalize_single_csv(csv_path)
        print(f"✔ Normalized: {csv_path.name}")

    print("✅ Phase-2.5 Normalization Complete")


if __name__ == "__main__":
    main()
