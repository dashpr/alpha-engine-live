import pandas as pd
from backtest.engines.phase5_portfolio_adapter import Phase5PortfolioAdapter
from backtest.engines.data_engine import HistoricalDataEngine
from backtest.engines.alpha_backtest_engine import AlphaBacktestEngine
from backtest.engines.portfolio_backtest_engine import PortfolioBacktestEngine


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
def load_data():
    engine = HistoricalDataEngine()
    return engine.run()


# ---------------------------------------------------------
# RUN ALPHA
# ---------------------------------------------------------
def run_alpha(df: pd.DataFrame):
    engine = AlphaBacktestEngine(
        top_n=20,
        rebalance_days=5,  # weekly
    )
    return engine.run(df)


# ---------------------------------------------------------
# RUN PORTFOLIO BACKTEST
# ---------------------------------------------------------
def run_portfolio(alpha_df: pd.DataFrame):
    engine = PortfolioBacktestEngine()
    return engine.run(alpha_df)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    print("🚀 Phase-5 Institutional Backtest Started (2010–2024)")

    df = load_data()

    print("\n📊 Historical Data Loaded")
    print(f"Rows     : {len(df):,}")
    print(f"Symbols  : {df['symbol'].nunique()}")
    print(f"Date span: {df['date'].min()} → {df['date'].max()}")

    alpha_df = run_alpha(df)

    print("\n📈 Alpha Portfolio Generated")
    print(f"Rows : {len(alpha_df):,}")
    print(f"Dates: {alpha_df['date'].nunique()}")

    metrics = run_portfolio(alpha_df)

    print("\n🏆 BACKTEST COMPLETE")
    print(metrics)


if __name__ == "__main__":
    main()
