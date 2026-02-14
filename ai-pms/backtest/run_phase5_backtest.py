import pandas as pd
import numpy as np
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


DATA_FOLDER = "data/raw"
START_YEAR = 2010
END_YEAR = 2026

MODELS = ["momentum", "mean_reversion", "ml_factor"]


# =========================================================
# Load historical data
# =========================================================
def load_data():
    print("📊 Loading historical data...")

    engine = HistoricalDataEngine()
    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique():,}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    return df


# =========================================================
# Run alpha model
# =========================================================
def run_alpha_model(df, model_name):
    print(f"\n🧠 Running Alpha Model → {model_name}")

    engine = AlphaBacktestEngine(model_name=model_name)
    alpha_df = engine.run(df)

    print(f"📈 Alpha rows: {len(alpha_df):,}")

    return alpha_df


# =========================================================
# Portfolio simulation
# =========================================================
def run_portfolio(alpha_df, model_name):
    print(f"💼 Portfolio simulation → {model_name}")

    engine = PortfolioBacktestEngine()
    equity_curve = engine.run(alpha_df)

    return equity_curve


# =========================================================
# Institutional metrics
# =========================================================
def compute_metrics(equity_curve: pd.DataFrame):
    """
    equity_curve must contain:
    date | equity
    """

    returns = equity_curve["equity"].pct_change().dropna()

    years = len(equity_curve) / 252

    cagr = (equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]) ** (1 / years) - 1
    vol = returns.std() * np.sqrt(252)
    sharpe = cagr / vol if vol != 0 else 0

    running_max = equity_curve["equity"].cummax()
    drawdown = equity_curve["equity"] / running_max - 1
    max_dd = drawdown.min()

    return {
        "cagr": cagr,
        "volatility": vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }


# =========================================================
# MAIN PHASE-5 RUNNER
# =========================================================
def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2026)")

    df = load_data()

    results = []

    for model in MODELS:
        alpha_df = run_alpha_model(df, model)
        equity_curve = run_portfolio(alpha_df, model)

        metrics = compute_metrics(equity_curve)
        metrics["model"] = model

        results.append(metrics)

    # -----------------------------------------------------
    # Results comparison
    # -----------------------------------------------------
    results_df = pd.DataFrame(results)

    print("\n📊 Phase-5 Backtest Results")
    print(results_df.round(4))

    # -----------------------------------------------------
    # Select best model
    # -----------------------------------------------------
    best_model = results_df.sort_values("cagr", ascending=False).iloc[0]["model"]

    print(f"\n🏆 BEST MODEL → {best_model}")

    # Save results
    Path("data/output").mkdir(parents=True, exist_ok=True)
    results_df.to_csv("data/output/phase5_model_comparison.csv", index=False)

    print("\n✅ Phase-5 Completed Successfully")


# =========================================================
if __name__ == "__main__":
    main()
