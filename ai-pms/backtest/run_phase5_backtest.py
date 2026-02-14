import pandas as pd
import numpy as np
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


DATA_FOLDER = "data/raw"
MODELS = ["momentum", "mean_reversion", "ml_factor"]


# =============================================================
# LOAD DATA
# =============================================================
def load_data():
    print("📊 Loading historical data...")

    engine = HistoricalDataEngine(DATA_FOLDER)
    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique():,}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    return df


# =============================================================
# RUN ALPHA MODEL
# =============================================================
def run_alpha_model(df, model_name):
    print(f"\n🧠 Running Alpha Model → {model_name}")

    engine = AlphaBacktestEngine(model_name=model_name)
    alpha_df = engine.run(df)

    print(f"📈 Alpha rows: {len(alpha_df):,}")

    return alpha_df


# =============================================================
# PORTFOLIO SIMULATION
# =============================================================
def run_portfolio(alpha_df, model_name):
    print(f"💼 Portfolio simulation → {model_name}")

    engine = PortfolioBacktestEngine()
    equity_curve = engine.run(alpha_df)

    return equity_curve


# =============================================================
# METRICS
# =============================================================
def compute_metrics(equity_curve: pd.DataFrame):

    if "equity" not in equity_curve.columns:
        raise ValueError("Equity curve missing 'equity' column")

    returns = equity_curve["equity"].pct_change().dropna()

    years = len(returns) / 252
    cagr = (equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]) ** (
        1 / years
    ) - 1

    vol = returns.std() * np.sqrt(252)
    sharpe = cagr / vol if vol != 0 else 0

    cummax = equity_curve["equity"].cummax()
    drawdown = equity_curve["equity"] / cummax - 1
    max_dd = drawdown.min()

    return {
        "cagr": float(cagr),
        "volatility": float(vol),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
    }


# =============================================================
# MAIN PHASE-5
# =============================================================
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

    results_df = pd.DataFrame(results)

    print("\n📊 FINAL MODEL COMPARISON")
    print(results_df.sort_values("cagr", ascending=False))

    best_model = results_df.sort_values("cagr", ascending=False).iloc[0]["model"]

    print(f"\n🏆 BEST MODEL → {best_model}")


if __name__ == "__main__":
    main()
