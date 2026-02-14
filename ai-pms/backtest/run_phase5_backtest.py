import pandas as pd
import numpy as np
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


DATA_FOLDER = "data/raw"


# -------------------------------------------------------------
# Load historical data
# -------------------------------------------------------------
def load_data():
    print("📊 Loading historical data...")

    engine = HistoricalDataEngine()
    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print("Rows     :", len(df))
    print("Symbols  :", df["symbol"].nunique())
    print("Date span:", df["date"].min(), "→", df["date"].max())

    return df


# -------------------------------------------------------------
# Run alpha model
# -------------------------------------------------------------
def run_alpha_model(df: pd.DataFrame, model_name: str) -> pd.DataFrame:

    print(f"\n🧠 Running Alpha Model → {model_name}")

    engine = AlphaBacktestEngine(model_name=model_name)
    alpha_df = engine.run(df)

    print("📈 Alpha rows:", len(alpha_df))

    return alpha_df


# -------------------------------------------------------------
# Portfolio simulation
# -------------------------------------------------------------
def run_portfolio(alpha_df: pd.DataFrame, model_name: str):

    print(f"💼 Portfolio simulation → {model_name}")

    engine = PortfolioBacktestEngine()
    equity_curve = engine.run(alpha_df)

    return equity_curve


# -------------------------------------------------------------
# Metrics
# -------------------------------------------------------------
def compute_metrics(equity_curve: pd.DataFrame):

    returns = equity_curve["returns"]

    cagr = (equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]) ** (
        252 / len(equity_curve)
    ) - 1

    sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-9)
    max_dd = equity_curve["drawdown"].min()

    return {
        "cagr": float(cagr),
        "sharpe": float(sharpe),
        "max_dd": float(max_dd),
    }


# -------------------------------------------------------------
# MAIN PHASE-5
# -------------------------------------------------------------
def main():

    print("🚀 Phase-5 Institutional Backtest Started (2010–2026)")

    df = load_data()

    models = ["momentum", "mean_reversion", "ml_factor"]

    results = []

    for model in models:

        alpha_df = run_alpha_model(df, model)
        equity_curve = run_portfolio(alpha_df, model)
        metrics = compute_metrics(equity_curve)

        metrics["model"] = model
        results.append(metrics)

    results_df = pd.DataFrame(results).sort_values("cagr", ascending=False)

    print("\n🏆 FINAL MODEL RANKING")
    print(results_df)

    best_model = results_df.iloc[0]["model"]

    print(f"\n🚀 BEST MODEL SELECTED → {best_model}")
    print("➡️ Stage-6 Capital Scaling Ready")


if __name__ == "__main__":
    main()
