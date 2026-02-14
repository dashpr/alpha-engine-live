"""
Phase-5 Institutional Backtest Comparator
14-Year realistic PMS simulation with real costs
"""

import pandas as pd
import numpy as np
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


# ============================================================
# CONFIG (institutional locked)
# ============================================================

START_DATE = "2010-01-01"
END_DATE = "2026-02-15"

REBAlANCE_DAYS = 5          # weekly
TOP_N = 20                  # portfolio size

BROKERAGE = 0.0015          # 0.15% round trip
SLIPPAGE = 0.0005           # 0.05%
CASH_DRAG = 0.05            # 5% idle


DATA_FOLDER = "data/raw/nifty300"


# ============================================================
# LOAD HISTORICAL DATA
# ============================================================

def load_data() -> pd.DataFrame:
    print("📊 Loading historical data...")

    engine = HistoricalDataEngine(data_folder=DATA_FOLDER)
    df = engine.run()

    df = df[(df["date"] >= START_DATE) & (df["date"] <= END_DATE)]

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique():,}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    return df


# ============================================================
# RUN ONE ALPHA MODEL
# ============================================================

def run_alpha_model(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    print(f"\n🧠 Running Alpha Model → {model_name}")

    engine = AlphaBacktestEngine(
        model_name=model_name,
        rebalance_days=REBAlANCE_DAYS,
        top_n=TOP_N,
    )

    alpha_df = engine.run(df)

    print(f"📈 Alpha rows: {len(alpha_df):,}")
    return alpha_df


# ============================================================
# RUN PORTFOLIO SIMULATION WITH COSTS
# ============================================================

def run_portfolio(alpha_df: pd.DataFrame, model_name: str) -> dict:
    print(f"💼 Portfolio simulation → {model_name}")

    engine = PortfolioBacktestEngine(
        brokerage=BROKERAGE,
        slippage=SLIPPAGE,
        cash_drag=CASH_DRAG,
    )

    metrics = engine.run(alpha_df)

    return metrics


# ============================================================
# MAIN PHASE-5 COMPARATOR
# ============================================================

def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2026)")

    df = load_data()

    # --------------------------------------------------------
    # Alpha models to compare
    # --------------------------------------------------------
    models = [
        "momentum",
        "mean_reversion",
        "ml_factor",
    ]

    results = []

    for model in models:
        alpha_df = run_alpha_model(df, model)
        metrics = run_portfolio(alpha_df, model)

        metrics["model"] = model
        results.append(metrics)

    results_df = pd.DataFrame(results)

    # --------------------------------------------------------
    # CIO decision logic
    # --------------------------------------------------------
    best_model = results_df.sort_values("cagr", ascending=False).iloc[0]["model"]

    results_df["verdict"] = "REJECTED"
    results_df.loc[results_df["model"] == best_model, "verdict"] = "CORE PMS"

    # second best = satellite
    if len(results_df) > 1:
        second = results_df.sort_values("cagr", ascending=False).iloc[1]["model"]
        results_df.loc[results_df["model"] == second, "verdict"] = "SATELLITE"

    # --------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------
    out_dir = Path("data/output/phase5")
    out_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(out_dir / "phase5_comparison.csv", index=False)

    print("\n🏆 PHASE-5 FINAL RESULTS")
    print(results_df.sort_values("cagr", ascending=False).to_string(index=False))

    print("\n📁 Saved → data/output/phase5/phase5_comparison.csv")


# ============================================================

if __name__ == "__main__":
    main()
