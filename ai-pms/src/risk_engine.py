import pandas as pd
import numpy as np


class RiskEngine:
    """
    Institutional risk engine with full CI safety.

    Guarantees:
    - never crashes on empty data
    - always returns valid risk metrics
    """

    def portfolio_volatility(self, weights: np.ndarray, cov: pd.DataFrame) -> float:
        if len(weights) == 0 or cov.empty:
            return 0.0

        return float(np.sqrt(weights.T @ cov.values @ weights))

    def value_at_risk(self, returns: pd.Series, level: float = 0.95) -> float:
        if returns is None or len(returns) == 0:
            return 0.0

        return float(np.percentile(returns, (1 - level) * 100))

    def build_risk_state(self, weights_df: pd.DataFrame, returns_df: pd.DataFrame):
        # ⭐ SAFETY 1 — empty weights
        if weights_df is None or len(weights_df) == 0:
            return pd.DataFrame({
                "portfolio_volatility": [0.0],
                "VaR_95": [0.0],
            })

        pivot = (
            returns_df
            .pivot(index="date", columns="symbol", values="ret_1d")
            .dropna(how="all")
        )

        # ⭐ SAFETY 2 — empty return history
        if pivot.empty:
            return pd.DataFrame({
                "portfolio_volatility": [0.0],
                "VaR_95": [0.0],
            })

        cov = pivot.cov()

        # Align weights with covariance symbols
        aligned_weights = (
            weights_df
            .set_index("symbol")
            .reindex(cov.index)
            .fillna(0)["weight"]
            .values
        )

        vol = self.portfolio_volatility(aligned_weights, cov)

        port_returns = pivot @ aligned_weights

        var_95 = self.value_at_risk(port_returns)

        return pd.DataFrame({
            "portfolio_volatility": [vol],
            "VaR_95": [var_95],
        })
