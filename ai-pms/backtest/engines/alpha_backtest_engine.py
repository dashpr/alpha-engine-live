import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional Alpha Backtest Engine
    -----------------------------------
    Converts alpha scores → portfolio returns → equity curve.
    """

    def __init__(self, rebalance_freq="W"):
        self.rebalance_freq = rebalance_freq

    # --------------------------------------------------
    # Core Backtest Runner
    # --------------------------------------------------
    def run(self, prices: pd.DataFrame, alpha: pd.DataFrame) -> pd.DataFrame:
        """
        prices columns: date, symbol, close
        alpha columns : date, symbol, alpha_score
        """

        df = prices.merge(alpha, on=["date", "symbol"], how="inner")

        # Sort properly
        df = df.sort_values(["symbol", "date"])

        # Daily returns
        df["ret"] = df.groupby("symbol")["close"].pct_change()

        # Rebalance weights weekly using alpha ranking
        df["week"] = df["date"].dt.to_period("W")

        weights = (
            df.groupby(["week", "symbol"])["alpha_score"]
            .mean()
            .groupby(level=0)
            .apply(lambda x: x / x.abs().sum())
            .rename("weight")
            .reset_index()
        )

        df = df.merge(weights, on=["week", "symbol"], how="left")

        # Portfolio daily return
        df["weighted_ret"] = df["ret"] * df["weight"]

        portfolio = (
            df.groupby("date")["weighted_ret"]
            .sum()
            .fillna(0)
            .to_frame("portfolio_ret")
        )

        # Equity curve
        portfolio["equity"] = (1 + portfolio["portfolio_ret"]).cumprod()

        return portfolio
