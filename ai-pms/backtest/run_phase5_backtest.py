"""
Phase-5 Institutional Backtest Runner
Runs full historical alpha → portfolio → metrics pipeline.
"""

import pandas as pd

from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


# ---------------------------------------------------------
# Load historical data
# ---------------------------------------------------------
def load_data() -> pd.DataFrame:
    engine = HistoricalDataEngine(data_path="data/raw")
    return engine.run()


# ---------------------------------------------------------
# Run alpha model backtest
# ---------------------------------------------------------
def run_alpha(df: pd.DataFrame) -> pd.DataFrame:
    engine = AlphaBacktestEngine()
    return engine.run(df)


# ---------------------------------------------------------
# Run portfolio simulation
# ---------------------------------------------------------
def run_portfolio(alpha_df: pd.DataFrame) -> dict:
    engine = PortfolioBacktestEngine()
    return engine.run(alpha_df)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():

    print("🚀 Phase-5 Institutional Backtest Started (2010–2024)")

    # 1️⃣ Load data
    df = load_data()

    # Safety check
    if df.empty:
        raise ValueError("Historical dataframe is empty")

    # 2️⃣ Alpha backtest
    alpha_df = run_alpha(df)

    # 3️⃣ Portfolio simulation
    metrics = run_portfolio(alpha_df)

    # 4️⃣ Print results
    print("\n📈 BACKTEST RESULTS")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("\n✅ Phase-5 Backtest Complete")


# ---------------------------------------------------------
if __name__ == "__main__":
    main()
