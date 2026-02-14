import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional Alpha Engine supporting:

    1. Momentum
    2. Mean Reversion
    3. ML Factor (simple cross-sectional model placeholder)

    Output columns:
    date | symbol | weight | ret
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

    # ---------------------------------------------------------
    # Momentum alpha
    # ---------------------------------------------------------
    def _momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret_20"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        df["rank"] = df.groupby("date")["ret_20"].rank(ascending=False)

        return df[df["rank"] <= self.top_n]

    # ---------------------------------------------------------
    # Mean reversion alpha
    # ---------------------------------------------------------
    def _mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret_5"] = (
            df.groupby("symbol")["close"]
            .pct_change(5)
        )

        df["rank"] = df.groupby("date")["ret_5"].rank(ascending=True)

        return df[df["rank"] <= self.top_n]

    # ---------------------------------------------------------
    # ML factor alpha (institutional placeholder)
    # ---------------------------------------------------------
    def _ml_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Simple cross-sectional ML proxy:
        Combines momentum + volatility normalization.
        (Real ML model will replace this in Phase-6)
        """
        df = df.copy()

        df["ret_20"] = df.groupby("symbol")["close"].pct_change(20)
        df["vol_20"] = df.groupby("symbol")["close"].pct_change().rolling(20).std()

        # ML score proxy
        df["ml_score"] = df["ret_20"] / (df["vol_20"] + 1e-6)

        df["rank"] = df.groupby("date")["ml_score"].rank(ascending=False)

        return df[df["rank"] <= self.top_n]

    # ---------------------------------------------------------
    # Create alpha based on model
    # ---------------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model_name == "momentum":
            return self._momentum(df)

        elif self.model_name == "mean_reversion":
            return self._mean_reversion(df)

        elif self.model_name == "ml_factor":
            return self._ml_factor(df)

        else:
            raise ValueError(f"Unknown alpha model: {self.model_name}")

    # ---------------------------------------------------------
    # Convert to portfolio weights
    # ---------------------------------------------------------
    def _to_weights(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Equal weight inside top-N
        df["weight"] = 1 / self.top_n

        # Forward return (next-day)
        df["ret"] = (
            df.groupby("symbol")["close"]
            .pct_change()
            .shift(-1)
        )

        return df[["date", "symbol", "weight", "ret"]].dropna()

    # ---------------------------------------------------------
    # Public runner
    # ---------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise ValueError("Historical dataframe is empty")

        alpha = self._create_alpha(df)
        alpha = self._to_weights(alpha)

        return alpha
