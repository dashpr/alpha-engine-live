import pandas as pd
import numpy as np

from engines.data_engine import HistoricalDataEngine
from engines.alpha_backtest_engine import AlphaBacktestEngine
from engines.portfolio_backtest_engine import PortfolioBacktestEngine


MODELS = ["momentum", "mean_reversion", "ml_factor"]


# ---------------------------------------------------------
def compute_metrics(equity_curve: pd.DataFrame) -> dict:
    returns = equity_curve["equity"].pct_change().dropna()

    cagr = (equity_curve["equity"].iloc[-1] / equity_curve["equity"].iloc[0]) ** (
        252 / len(returns)
    ) - 1

    sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-9)

    drawdown = equity_curve["equity"] / equity_curve["equity"].cummax() - 1
    max_dd = drawdown.min()

    return {"cagr": cagr, "sharpe": sharpe, "max_dd": max_dd}


# ---------------------------------------------------------
def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2026)")

    # ---------- Load Data ----------
    df = HistoricalDataEngine().run()

    results = []

    # ---------- Run Models ----------
    for model in MODELS:
        alpha_df = AlphaBacktestEngine(model).run(df)

        equity_curve = PortfolioBacktestEngine().run(alpha_df)

        metrics = compute_metrics(equity_curve)
        metrics["model"] = model

        results.append(metrics)

    # ---------- Compare ----------
    results_df = pd.DataFrame(results).sort_values("cagr", ascending=False)

    print("\n🏆 Model Comparison")
    print(results_df.round(4))

    best = results_df.iloc[0]["model"]
    print(f"\n✅ Phase-5 Winner → {best}")


# ---------------------------------------------------------
if __name__ == "__main__":
    main()
