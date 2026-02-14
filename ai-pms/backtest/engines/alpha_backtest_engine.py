import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional Alpha Backtest Engine
    Supports multiple alpha models:
        - momentum
        - mean_reversion
        - volatility_breakout
    """

    def __init__(
        self,
        model_name: str = "momentum",
        rebalance_days: int = 5,
        top_n: int = 20,
    ):
        self.model_name = model_name
        self.rebalance_days = int(rebalance_days)
        self.top_n = int(top_n)

    # ------------------------------------------------------------------
    # Alpha model factory
    # ------------------------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model_name == "momentum":
            return self._momentum_alpha(df)

        elif self.model_name == "mean_reversion":
            return self._mean_reversion_alpha(df)

        elif self.model_name == "volatility_breakout":
            return self._volatility_breakout_alpha(df)

        else:
            raise ValueError(f"Unknown alpha model: {self.model_name}")

    # ------------------------------------------------------------------
    # Model 1 → Momentum
    # ------------------------------------------------------------------
    def _momentum_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret_20"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        return df

    # ------------------------------------------------------------------
    # Model 2 → Mean Reversion
    # ------------------------------------------------------------------
    def _mean_reversion_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret_5"] = df.groupby("symbol")["close"].pct_change(5)
        df["alpha"] = -df["ret_5"]

        return df

    # ------------------------------------------------------------------
    # Model 3 → Volatility Breakout
    # ------------------------------------------------------------------
    def _volatility_breakout_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        rolling_std = (
            df.groupby("symbol")["close"]
            .pct_change()
            .rolling(20)
            .std()
            .reset_index(level=0, drop=True)
        )

        df["alpha"] = rolling_std

        return df

    # ------------------------------------------------------------------
    # Portfolio construction
    # ------------------------------------------------------------------
    def _build_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "alpha" not in df.columns:
            # momentum case
            df["alpha"] = df["ret_20"]

        # Weekly rebalance
        df["rank"] = (
            df.groupby("date")["alpha"]
            .rank(ascending=False, method="first")
        )

        df = df[df["rank"] <= self.top_n]

        df["weight"] = 1.0 / self.top_n

        # Forward return
        df["ret"] = (
            df.groupby("symbol")["close"]
            .pct_change()
            .shift(-1)
        )

        return df[["date", "symbol", "weight", "ret"]].dropna()

    # ------------------------------------------------------------------
    # Public run
    # ------------------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise ValueError("Historical dataframe is empty")

        df = self._create_alpha(df)
        df = self._build_portfolio(df)

        return df
