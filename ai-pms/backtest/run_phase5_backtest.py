"""
AI-PMS — PHASE-5 FROZEN INSTITUTIONAL BACKTEST
FINAL STABLE PRODUCTION VERSION

Properties:
• Uses only raw CSV history
• Robust to NSE/Yahoo CSV format variations
• No preprocessing / normalization step
• Deterministic weekly backtest
• Institutional cost model
• Reproducible equity + checksum
"""

from pathlib import Path
import hashlib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[2]
AIPMS_ROOT = REPO_ROOT / "ai-pms"

RAW_DATA_DIR = AIPMS_ROOT / "data" / "raw"
OUTPUT_DIR = AIPMS_ROOT / "data" / "output" / "phase5"


# ============================================================
# CONFIG (FROZEN)
# ============================================================

START_DATE = "2010-01-01"
PORTFOLIO_SIZE = 15
INITIAL_CAPITAL = 1.0

BROKERAGE = 0.001
SLIPPAGE = 0.001
IMPACT = 0.0005
TOTAL_COST = BROKERAGE + SLIPPAGE + IMPACT


# ============================================================
# UNIVERSAL CSV PARSING
# ============================================================

def _extract_date(df: pd.DataFrame):
    """Find date in column, index, or first column."""

    for col in ["date", "Date", "DATE"]:
        if col in df.columns:
            return pd.to_datetime(df[col], errors="coerce")

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


def _extract_close(df: pd.DataFrame):
    """Find close price from common variants."""

    for col in [
        "close", "Close", "CLOSE",
        "adj close", "Adj Close",
        "price", "Price"
    ]:
        if col in df.columns:
            return pd.to_numeric(df[col], errors="coerce")

    return None


def _canonical_date(series):
    """Force strict YYYY-MM-DD pandas datetime."""

    series = pd.to_datetime(series, errors="coerce")

    # Works for Series or DatetimeIndex
    if isinstance(series, pd.Series):
        return series.dt.normalize()

    return pd.to_datetime(series).normalize()


def load_prices() -> pd.DataFrame:
    """Load and canonicalize all CSVs in memory."""

    files = list(RAW_DATA_DIR.glob("*.csv"))
    if not files:
        raise RuntimeError(f"No CSV files found in {RAW_DATA_DIR}")

    frames = []

    for f in files:
        df = pd.read_csv(f)

        date = _extract_date(df)
        close = _extract_close(df)

        if date is None or close is None:
            print(f"⚠ Skipping {f.name} → cannot parse date/close")
            continue

        cleaned = pd.DataFrame({
            "date": _canonical_date(date),
            "ticker": f.stem.upper(),
            "close": close,
        }).dropna()

        if not cleaned.empty:
            frames.append(cleaned)

    if not frames:
        raise RuntimeError("No valid price data after parsing.")

    df = pd.concat(frames, ignore_index=True)

    return (
        df.drop_duplicates(["date", "ticker"])
        .sort_values(["date", "ticker"])
        .reset_index(drop=True)
    )


# ============================================================
# FEATURES
# ============================================================

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    returns = df.groupby("ticker")["close"].pct_change()

    df["ret_5d"] = df.groupby("ticker")["close"].pct_change(5)
    df["ret_20d"] = df.groupby("ticker")["close"].pct_change(20)
    df["ret_60d"] = df.groupby("ticker")["close"].pct_change(60)

    df["vol_20d"] = (
        returns.groupby(df["ticker"])
        .rolling(20)
        .std()
        .reset_index(level=0, drop=True)
    )

    return df.dropna().reset_index(drop=True)


# ============================================================
# ALPHA (RULE-BASED ONLY)
# ============================================================

def compute_alpha(df: pd.DataFrame) -> pd.DataFrame:
    momentum = 0.6 * df["ret_60d"] + 0.4 * df["ret_20d"]
    mean_rev = -df["ret_5d"] / df["vol_20d"]

    df["alpha_score"] = (
        0.5 * momentum.groupby(df["date"]).rank(pct=True)
        + 0.5 * mean_rev.groupby(df["date"]).rank(pct=True)
    )

    return df


# ============================================================
# BACKTEST
# ============================================================

def run_backtest(df: pd.DataFrame) -> pd.DataFrame:

    weekly_dates = (
        df["date"]
        .drop_duplicates()
        .sort_values()
        .to_series()
        .dt.to_period("W-FRI")
        .drop_duplicates()
        .dt.end_time
    )

    equity = INITIAL_CAPITAL
    current_weights = {}
    equity_curve = []

    for date in weekly_dates:

        day = df[df["date"] <= date]
        if day.empty:
            continue

        latest = day.sort_values("date").groupby("ticker").tail(1)
        latest = latest.sort_values("alpha_score", ascending=False)

        selected = latest.head(PORTFOLIO_SIZE)
        if selected.empty:
            continue

        target_weight = 1.0 / PORTFOLIO_SIZE
        new_weights = {t: target_weight for t in selected["ticker"]}

        turnover = sum(
            abs(new_weights.get(t, 0) - current_weights.get(t, 0))
            for t in set(new_weights) | set(current_weights)
        )

        equity -= equity * turnover * TOTAL_COST

        weekly_ret = selected["ret_5d"].mean()
        equity *= (1 + weekly_ret)

        equity_curve.append({"date": date, "equity": equity})
        current_weights = new_weights

    return pd.DataFrame(equity_curve)


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(equity_curve: pd.DataFrame):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    equity_path = OUTPUT_DIR / "equity_curve.csv"
    equity_curve.to_csv(equity_path, index=False)

    checksum = hashlib.sha256(equity_path.read_bytes()).hexdigest()
    (OUTPUT_DIR / "equity_checksum.txt").write_text(checksum)


# ============================================================
# MAIN
# ============================================================

def main():
    print("▶ Phase-5 Institutional Backtest Started")

    df = load_prices()
    df = build_features_
