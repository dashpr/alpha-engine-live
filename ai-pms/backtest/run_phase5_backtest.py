# ai-pms/backtest/run_phase5_backtest.py

import pandas as pd

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


DATA_FOLDER = "data/raw"


# ---------- METRICS ----------

def compute_metrics(equity_curve: pd.DataFrame) -> dict:
    returns = equity_curve["equity"].pct_change().dropna()

    cagr = (equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]) ** (
        252 / len(returns)
    ) - 1

    vol = returns.std() * (252**0.5)
    sharpe = cagr / vol if vol != 0 else 0

    dd = equity_curve["equity"] / equity_curve["equity"].cummax() - 1
    max_dd = dd.min()

    return {"cagr": cagr, "sharpe": sharpe, "max_dd": max_dd}


# ---------- PIPELINE ----------

def load_data() -> pd.DataFrame:
    print("📊 Loading historical data...")
    engine = HistoricalDataEngine(DATA_FOLDER)
    df = engine.run()

    print("\n📊 Historical Data Loaded")
    print("Rows     :", len(df))
    print("Symbols  :", df["symbol"].nunique())
    print("Date span:", df["date"].min(), "→", df["date"].max())

    return df


def run_alpha_model(df: pd.DataFrame, model: str) -> pd.DataFrame:
    print(f"\n🧠 Running Alpha Model → {model}")
    engine = AlphaBacktestEngine(model_name=model)
    alpha_df = engine.run(df)
    print("📈 Alpha rows:", len(alpha_df))
    return alpha_df


def run_portfolio(alpha_df: pd.DataFrame, model: str) -> pd.DataFrame:
    print(f"💼 Portfolio simulation → {model}")
    engine = PortfolioBacktestEngine()
    return engine.run(alpha_df)


# ---------- MAIN ----------

def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2026)")

    df = load_data()

    models = ["momentum", "mean_reversion", "ml_factor"]
    results = []

    for m in models:
        alpha_df = run_alpha_model(df, m)
        equity = run_portfolio(alpha_df, m)
        metrics = compute_metrics(equity)

        metrics["model"] = m
        results.append(metrics)

    results_df = pd.DataFrame(results)
    print("\n📊 Model Comparison\n")
    print(results_df)

    best = results_df.sort_values("cagr", ascending=False).iloc[0]
    print(f"\n🏆 Best Model → {best['model']} | CAGR: {best['cagr']:.2%}")


if __name__ == "__main__":
    main()
