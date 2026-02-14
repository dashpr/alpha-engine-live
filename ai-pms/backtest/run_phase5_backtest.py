import json
import pandas as pd
from pathlib import Path

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine
from backtest.reality.transaction_cost_engine import TransactionCostEngine
from backtest.reality.slippage_liquidity_engine import SlippageLiquidityEngine
from backtest.reality.turnover_governor import TurnoverGovernor
from backtest.reality.drawdown_scaler import DrawdownScaler
from backtest.reality.stress_test_engine import StressTestEngine


OUTPUT_DIR = Path("data/output/phase5")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# STEP 1 — LOAD 14Y DATA
# ---------------------------------------------------
def load_data():
    engine = HistoricalDataEngine(
        start_date="2010-01-01",
        end_date="2024-12-31",
        universe="top200",
    )
    return engine.run()


# ---------------------------------------------------
# STEP 2 — RUN ALPHA BACKTEST
# ---------------------------------------------------
def run_alpha(df):
    engine = AlphaBacktestEngine(
        top_n=25,
        rebalance="weekly",
    )
    return engine.run(df)


# ---------------------------------------------------
# STEP 3 — APPLY REALITY ENGINES
# ---------------------------------------------------
def apply_reality(portfolio_df):
    portfolio_df = TransactionCostEngine().apply(portfolio_df)
    portfolio_df = SlippageLiquidityEngine().apply(portfolio_df)
    portfolio_df = TurnoverGovernor().apply(portfolio_df)
    portfolio_df = DrawdownScaler().apply(portfolio_df)
    return portfolio_df


# ---------------------------------------------------
# STEP 4 — BUILD EQUITY CURVE
# ---------------------------------------------------
def build_equity_curve(df):
    engine = PortfolioBacktestEngine(initial_capital=100_000)
    equity = engine.run(df)
    return equity


# ---------------------------------------------------
# STEP 5 — METRICS
# ---------------------------------------------------
def compute_metrics(equity: pd.DataFrame):
    returns = equity["equity"].pct_change().dropna()

    years = (equity.index[-1] - equity.index[0]).days / 365.25
    cagr = (equity["equity"].iloc[-1] / equity["equity"].iloc[0]) ** (1 / years) - 1

    max_dd = (equity["equity"] / equity["equity"].cummax() - 1).min()

    sharpe = returns.mean() / returns.std() * (252 ** 0.5)
    sortino = returns.mean() / returns[returns < 0].std() * (252 ** 0.5)

    return {
        "CAGR": float(cagr),
        "Max Drawdown": float(max_dd),
        "Sharpe": float(sharpe),
        "Sortino": float(sortino),
    }


# ---------------------------------------------------
# STEP 6 — STRESS TESTS
# ---------------------------------------------------
def run_stress_tests(equity):
    engine = StressTestEngine()
    return engine.run_all(equity)


# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------
def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2024)")

    df = load_data()
    alpha_df = run_alpha(df)
    reality_df = apply_reality(alpha_df)
    equity = build_equity_curve(reality_df)

    metrics = compute_metrics(equity)
    stress = run_stress_tests(equity)

    # Save outputs
    equity.to_csv(OUTPUT_DIR / "equity_curve.csv")

    with open(OUTPUT_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    with open(OUTPUT_DIR / "stress_tests.json", "w") as f:
        json.dump(stress, f, indent=2)

    print("✅ Phase-5 Backtest Complete")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
