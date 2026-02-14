"""
PHASE-5 INSTITUTIONAL MODEL COMPARISON ENGINE
---------------------------------------------

Runs 3 alpha models on the SAME historical data
and produces institutional decision metrics.

Output:
data/output/phase5/model_comparison.parquet
data/output/phase5/cio_decision_table.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


OUTPUT_DIR = Path("data/output/phase5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Load Historical Data (14Y institutional window)
# ============================================================
def load_data():
    print("📊 Loading 14-year institutional data...")

    engine = HistoricalDataEngine()
    df = engine.run()

    if df.empty:
        raise ValueError("Historical dataframe is empty")

    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique():,}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    return df


# ============================================================
# Run Alpha Model
# ============================================================
def run_alpha(df, model_name):
    print(f"\n🧠 Running {model_name}...")

    engine = AlphaBacktestEngine(model_type=model_name)
    alpha_df = engine.run(df)

    if alpha_df.empty:
        raise ValueError(f"{model_name} produced empty alpha")

    return alpha_df


# ============================================================
# Run Portfolio Backtest
# ============================================================
def run_portfolio(alpha_df, model_name):
    print(f"📈 Backtesting portfolio → {model_name}")

    engine = PortfolioBacktestEngine()
    metrics = engine.run(alpha_df)

    metrics["model"] = model_name
    return metrics


# ============================================================
# Institutional Metrics Table
# ============================================================
def build_decision_table(results):
    df = pd.DataFrame(results)

    df = df[
        [
            "model",
            "cagr",
            "volatility",
            "sharpe",
            "sortino",
            "max_drawdown",
            "recovery_days",
            "turnover",
            "cost_impact",
        ]
    ].sort_values("sharpe", ascending=False)

    return df


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n🚀 PHASE-5 INSTITUTIONAL MODEL COMPARISON STARTED\n")

    df = load_data()

    models = ["conservative", "hybrid", "aggressive"]
    results = []

    for m in models:
        alpha_df = run_alpha(df, m)
        metrics = run_portfolio(alpha_df, m)
        results.append(metrics)

    # --------------------------------------------------------
    # Save full comparison
    # --------------------------------------------------------
    comparison_df = pd.DataFrame(results)
    comparison_path = OUTPUT_DIR / "model_comparison.parquet"
    comparison_df.to_parquet(comparison_path, index=False)

    # --------------------------------------------------------
    # CIO Decision Table
    # --------------------------------------------------------
    decision_df = build_decision_table(results)
    decision_path = OUTPUT_DIR / "cio_decision_table.csv"
    decision_df.to_csv(decision_path, index=False)

    print("\n✅ PHASE-5 COMPLETE")
    print(f"Saved → {comparison_path}")
    print(f"Saved → {decision_path}")

    print("\n🏆 CIO DECISION TABLE\n")
    print(decision_df.to_string(index=False))


if __name__ == "__main__":
    main()
