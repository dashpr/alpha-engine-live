"""
AI-PMS — PHASE-5 FROZEN INSTITUTIONAL BACKTEST
Monorepo-native • Deterministic • CI-safe • Final
"""

import hashlib
from pathlib import Path
import pandas as pd


# ============================================================
# CONFIGURATION (FROZEN)
# ============================================================

CURRENT_FILE = Path(__file__).resolve()

# repo root
REPO_ROOT = CURRENT_FILE.parents[2]

# ai-pms root (monorepo scoped)
AIPMS_ROOT = REPO_ROOT / "ai-pms"

RAW_DATA_DIR = AIPMS_ROOT / "data" / "raw"
OUTPUT_DIR = AIPMS_ROOT / "data" / "output" / "phase5"

START_DATE = "2010-01-01"
PORTFOLIO_SIZE = 15
INITIAL_CAPITAL = 1.0

BROKERAGE = 0.001
SLIPPAGE = 0.001
IMPACT = 0.0005
TOTAL_COST = BROKERAGE + SLIPPAGE + IMPACT


# ============================================================
# STEP-1: LOAD RAW PRICE DATA
# ============================================================

REQUIRED_COLUMNS = {"date", "ticker", "close"}


def load_prices() -> pd.DataFrame:
    files = list(RAW_DATA_DIR.glob("*.csv"))

    if not files:
        raise RuntimeError(
            f"❌ No CSV files found in expected path:\n{RAW_DATA_DIR}"
        )

    frames = []
    for f in files:
        df = pd.read_csv(f)

        if not REQUIRED_COLUMNS.issubset(df.columns):
            raise RuntimeError(f"❌ Schema violation in {f.name}")

        frames.append(df[["date", "ticker", "close"]])

    df = pd.concat(frames, ignore_index=True)

    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= START_DATE]

    return df.sort_values(["date", "ticker"]).reset_index(drop=True)


# ============================================================
# STEP-2: FEATURES
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
# STEP-3: RULE-BASED ALPHA
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
# STEP-4: WEEKLY BACKTEST
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
# STEP-5: SAVE OUTPUTS
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
    df = build_features(df)
    df = compute_alpha(df)

    equity_curve = run_backtest(df)
    save_outputs(equity_curve)

    print("✅ Phase-5 Backtest Complete")
    print(f"📁 Output saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
