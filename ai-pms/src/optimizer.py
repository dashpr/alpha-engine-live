import pandas as pd
import numpy as np
import cvxpy as cp


class PortfolioOptimizer:
    """
    Hybrid institutional optimizer:
    - Mean‑variance objective
    - Weight constraints
    - Risk stabilisation
    """

    def __init__(self, max_weight: float = 0.1):
        self.max_weight = max_weight

    def optimize(self, alpha_df: pd.DataFrame, cov_matrix: pd.DataFrame):
        assets = alpha_df["symbol"].values
        mu = alpha_df["alpha_score"].values
        Sigma = cov_matrix.values

        n = len(mu)
        w = cp.Variable(n)

        objective = cp.Maximize(mu @ w - 0.5 * cp.quad_form(w, Sigma))

        constraints = [
            cp.sum(w) == 1,
            w >= 0,
            w <= self.max_weight,
        ]

        prob = cp.Problem(objective, constraints)
        prob.solve()

        return pd.DataFrame({
            "symbol": assets,
            "weight": w.value
        })
