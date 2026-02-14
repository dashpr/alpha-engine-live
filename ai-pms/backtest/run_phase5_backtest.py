"""
PHASE-5 INSTITUTIONAL BACKTEST
--------------------------------
Runs full historical simulation on:

• Nifty-300 universe (CSV based)
• Real OHLCV data since 2010
• Phase-3 Alpha → Portfolio → Metrics

Outputs:
→ CAGR
→ Sharpe
→ Max Drawdown
→ Equity Curve
→ Saved institutional metrics
"""

import pandas as pd
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


# ============================================================
# CONFIG
# ============================================================

START_DATE = "2010-01-01"
END_DATE = "2026-12-31"

UNIVERSE_NAME = "NIFTY_300"

DATA_FOLDER = Path("data/raw/nse/")
OUTPUT_FOLDER = Path("data/output/phase5/")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


# ============================================================
# STEP 1 — LOAD HISTORICAL DATA
# ============================================================

def load_data() -> pd.DataFrame:
    """Load real NSE historical data."""

    engine = HistoricalDataEngine(
        data_folder=DATA_FOLDER,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique()}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    return df


# ============================================================
# STEP 2 — RUN ALPHA ENGINE
# ============================================================

def run_alpha(df: pd.DataFrame) -> pd.DataFrame:
    """Generate alpha portfolio from historical prices."""

    engine = AlphaBacktestEngine(
        top_n=20,
        rebalance_days=5,      # weekly rebalance
        min_history_days=60,
    )

    alpha_df = engine.run(df)

    print("\n📈 Alpha Portfolio Generated")
    print(f"Rows : {len(alpha_df):,}")
    print(f"Dates: {alpha_df['date'].nunique()}")

    return alpha_df


# ============================================================
# STEP 3 — PORTFOLIO BACKTEST
# ============================================================

def run_portfolio(alpha_df: pd.DataFrame) -> dict:
    """Convert alpha weights into equity curve & metrics."""

    engine = PortfolioBacktestEngine(
        initial_capital=100_000,
        transaction_cost_bps=10,
        slippage_bps=5,
    )

    metrics = engine.run(alpha_df)

    print("\n💰 Portfolio Backtest Complete")
    print(f"CAGR        : {metrics['cagr']:.2%}")
    print(f"Sharpe      : {metrics['sharpe']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")

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
    print("\n🚀 Phase-5 Institutional Backtest Started (2010–2024)")

    df = load_data()
    alpha_df = run_alpha(df)
    metrics = run_portfolio(alpha_df)

    save_results(metrics)

    print("\n✅ PHASE-5 BACKTEST COMPLETE\n")


# ============================================================

if __name__ == "__main__":
    main()
