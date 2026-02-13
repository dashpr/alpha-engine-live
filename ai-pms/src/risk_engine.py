import pandas as pd
import numpy as np


class RiskEngine:
    """
    Computes institutional daily risk metrics.
    """

    def portfolio_volatility(self, weights: np.ndarray, cov: pd.DataFrame) -> float:
        return float(np.sqrt(weights.T @ cov.values @ weights))

    def value_at_risk(self, returns: pd.Series, level: float = 0.95) -> float:
        return float(np.percentile(returns, (1 - level) * 100))

    def build_risk_state(self, weights_df: pd.DataFrame, returns_df: pd.DataFrame):
        pivot = returns_df.pivot(index="date", columns="symbol", values="ret_1d").dropna()

        cov = pivot.cov()
        w = weights_df.set_index("symbol").loc[cov.index]["weight"].values

        vol = self.portfolio_volatility(w, cov)
        port_returns = pivot @ w
        var_95 = self.value_at_risk(port_returns)

        return pd.DataFrame({
            "portfolio_volatility": [vol],
            "VaR_95": [var_95],
        })
