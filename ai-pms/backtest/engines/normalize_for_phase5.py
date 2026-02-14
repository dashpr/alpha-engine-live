"""
AI-PMS Phase-2.5 Normalization Engine
-------------------------------------

Purpose:
Convert raw NSE OHLCV CSV files into
Phase-5 institutional backtest schema:

    date,ticker,close

Design principles:
- Deterministic
- No ML / no features
- No look-ahead
- Safe overwrite
- CI compatible
"""

from pathlib import Path
import pandas as pd


# ============================================================
# PATH CONFIGURATION (MONOREPO SAFE)
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[3]
AIPMS_ROOT = REPO_ROOT / "ai-pms"

RAW_DATA_DIR = AIPMS_ROOT / "data" / "raw"


# ============================================================
# NORMALIZATION LOGIC
# ============================================================

def normalize_single_csv(csv_path: Path) -> None:
    """
    Convert one OHLCV CSV → Phase-5 schema.
    Overwrites file in-place (safe deterministic transform).
    """

    df = pd.read_csv(csv_path)

    # --------------------------------------------------------
    # Detect column naming variations from NSE / Yahoo formats
    # --------------------------------------------------------
    column_map = {
        "Date": "date",
        "date": "date",
        "Close": "close",
        "close": "close",
        "Adj Close": "close",
        "adj_close": "close",
    }

    df = df.rename(columns=column_map)

    # --------------------------------------------------------
    # Validate required source columns
    # --------------------------------------------------------
    if "date" not in df.columns or "close" not in df.columns:
        raise RuntimeError(
            f"❌ Cannot normalize {csv_path.name} → missing Date/Close columns"
        )

    # --------------------------------------------------------
    # Build Phase-5 schema
    # --------------------------------------------------------
    ticker = csv_path.stem.upper()

    normalized = pd.DataFrame({
        "date": pd.to_datetime(df["date"]),
        "ticker": ticker,
        "close": df["close"].astype(float),
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

    # --------------------------------------------------------
    # Overwrite original CSV safely
    # --------------------------------------------------------
    normalized.to_csv(csv_path, index=False)


# ============================================================
# MAIN NORMALIZATION RUNNER
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
