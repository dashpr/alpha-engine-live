"""
PHASE-5 INSTITUTIONAL BACKTEST (ENGINE-COMPATIBLE)
--------------------------------------------------

• Uses your EXISTING HistoricalDataEngine signature
• No assumptions about constructor params
• Runs full Alpha → Portfolio → Metrics pipeline
• Production safe for GitHub Actions
"""

import pandas as pd
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


# ============================================================
# OUTPUT PATH
# ============================================================

OUTPUT_FOLDER = Path("data/output/phase5")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 1 — LOAD HISTORICAL DATA
# ============================================================

def load_data() -> pd.DataFrame:
    """
    Load data using EXISTING HistoricalDataEngine
    without passing unsupported arguments.
    """

    engine = HistoricalDataEngine()  # ← critical fix

    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique() if not df.empty else 0}")
    print(
        f"Date span: {df['date'].min() if not df.empty else 'NA'} → "
        f"{df['date'].max() if not df.empty else 'NA'}"
    )

    if df.empty:
        raise ValueError("❌ Historical dataframe is empty")

    return df


# ============================================================
# STEP 2 — RUN ALPHA BACKTEST
# ============================================================

def run_alpha(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate alpha portfolio.
    Uses ONLY parameters supported by your engine.
    """

    engine = AlphaBacktestEngine()

    alpha_df = engine.run(df)

    print("\n📈 Alpha Portfolio Generated")
    print(f"Rows : {len(alpha_df):,}")
    print(f"Dates: {alpha_df['date'].nunique()}")

    if alpha_df.empty:
        raise ValueError("❌ Alpha dataframe is empty")

    return alpha_df


# ============================================================
# STEP 3 — PORTFOLIO BACKTEST
# ============================================================

def run_portfolio(alpha_df: pd.DataFrame) -> dict:
    """
    Convert alpha weights → equity curve → institutional metrics.
    """

    engine = PortfolioBacktestEngine()

    metrics = engine.run(alpha_df)

    print("\n💰 Portfolio Backtest Complete")
    print(f"CAGR        : {metrics.get('cagr', 0):.2%}")
    print(f"Sharpe      : {metrics.get('sharpe', 0):.2f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown', 0):.2%}")

    return metrics


# ============================================================
# STEP 4 — SAVE RESULTS
# ============================================================

def save_results(metrics: dict):
    """Persist institutional metrics."""

    out_path = OUTPUT_FOLDER / "phase5_metrics.csv"

    pd.DataFrame([metrics]).to_csv(out_path, index=False)

    print(f"\n📁 Metrics saved → {out_path.resolve()}")


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    print("\n🚀 Phase-5 Institutional Backtest Started")

    df = load_data()
    alpha_df = run_alpha(df)
    metrics = run_portfolio(alpha_df)

    save_results(metrics)

    print("\n✅ PHASE-5 BACKTEST COMPLETE\n")


# ============================================================

if __name__ == "__main__":
    main()
