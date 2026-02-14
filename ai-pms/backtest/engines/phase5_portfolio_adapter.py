"""
Phase-5 Portfolio Adapter
Converts Phase-3/4 weights + historical prices
into institutional backtest-ready return stream.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


class Phase5PortfolioAdapter:
    """
    Creates portfolio return dataframe required by PortfolioBacktestEngine.

    Output columns:
        date
        ret
        weight
    """

    def __init__(
        self,
        weights_path: str = "data/output/final_weights.parquet",
    ):
        self.weights_path = Path(weights_path)

    # ------------------------------------------------------------------ #
    # Load weights
    # ------------------------------------------------------------------ #
    def _load_weights(self) -> pd.DataFrame:
        if not self.weights_path.exists():
            raise FileNotFoundError(f"Weights file not found: {self.weights_path}")

        df = pd.read_parquet(self.weights_path)

        required = {"date", "symbol", "weight"}
        if not required.issubset(df.columns):
            raise ValueError(f"Weights file must contain columns: {required}")

        df["date"] = pd.to_datetime(df["date"])
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

        return df.dropna(subset=["date", "symbol", "weight"])

    # ------------------------------------------------------------------ #
    # Merge with historical prices
    # ------------------------------------------------------------------ #
    def _merge_prices(
        self,
        weights: pd.DataFrame,
        prices: pd.DataFrame,
    ) -> pd.DataFrame:
        required_price_cols = {"date", "symbol", "close"}
        if not required_price_cols.issubset(prices.columns):
            raise ValueError(f"Price DF must contain columns: {required_price_cols}")

        prices = prices.copy()
        prices["date"] = pd.to_datetime(prices["date"])
        prices["close"] = pd.to_numeric(prices["close"], errors="coerce")

        # Sort for return calc
        prices = prices.sort_values(["symbol", "date"])

        # Daily returns per stock
        prices["ret"] = prices.groupby("symbol")["close"].pct_change()

        # Merge with weights
        df = weights.merge(
            prices[["date", "symbol", "ret"]],
            on=["date", "symbol"],
            how="left",
        )

        return df.dropna(subset=["ret"])

    # ------------------------------------------------------------------ #
    # Aggregate to portfolio return
    # ------------------------------------------------------------------ #
    def _portfolio_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Weighted return per day
        df["weighted_ret"] = df["weight"] * df["ret"]

        portfolio = (
            df.groupby("date")
            .agg(
                ret=("weighted_ret", "sum"),
                weight=("weight", "sum"),
            )
            .reset_index()
            .sort_values("date")
        )

        return portfolio.dropna(subset=["ret"])

    # ------------------------------------------------------------------ #
    # Public run method
    # ------------------------------------------------------------------ #
    def run(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Parameters
        ----------
        prices : pd.DataFrame
            Historical OHLCV dataframe from Phase-5 data engine.

        Returns
        -------
        pd.DataFrame
            Columns: date | ret | weight
        """

        weights = self._load_weights()
        merged = self._merge_prices(weights, prices)
        portfolio = self._portfolio_returns(merged)

        if portfolio.empty:
            raise ValueError("Portfolio return dataframe is empty")

        return portfolio
