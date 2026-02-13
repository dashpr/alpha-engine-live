import pandas as pd
import numpy as np
import cvxpy as cp


class PortfolioOptimizer:
    """
    Hybrid institutional optimizer with CI safety.

    Handles:
    - empty alpha universe
    - insufficient covariance
    - solver failures

    Always returns valid weights.
    """

    def __init__(self, max_weight: float = 0.1):
        self.max_weight = max_weight

    def _equal_weight_fallback(self, symbols):
        n = len(symbols)

        if n == 0:
            # Ultimate safety fallback
            return pd.DataFrame({
                "symbol": [],
                "weight": []
            })

        weights = np.ones(n) / n
        return pd.DataFrame({
            "symbol": symbols,
            "weight": weights
        })

    def optimize(self, alpha_df: pd.DataFrame, cov_matrix: pd.DataFrame):
        # ⭐ SAFETY 1 — empty alpha
        if alpha_df is None or len(alpha_df) == 0:
            print("⚠️ Empty alpha universe → using equal-weight fallback.")
            return self._equal_weight_fallback([])

        assets = alpha_df["symbol"].values
        mu = alpha_df["alpha_score"].fillna(0).values

        # ⭐ SAFETY 2 — covariance mismatch
        if cov_matrix is None or cov_matrix.empty:
            print("⚠️ Missing covariance → equal-weight fallback.")
            return self._equal_weight_fallback(assets)

        # Align covariance with assets
        cov_matrix = cov_matrix.reindex(index=assets, columns=assets).fillna(0)
        Sigma = cov_matrix.values

        n = len(mu)

        # ⭐ SAFETY 3 — too few assets
        if n < 2:
            print("⚠️ Too few assets for optimization → equal-weight fallback.")
            return self._equal_weight_fallback(assets)

        try:
            w = cp.Variable(n)

            objective = cp.Maximize(mu @ w - 0.5 * cp.quad_form(w, Sigma))

            constraints = [
                cp.sum(w) == 1,
                w >= 0,
                w <= self.max_weight,
            ]

            prob = cp.Problem(objective, constraints)
            prob.solve()

            # ⭐ SAFETY 4 — solver failure
            if w.value is None:
                print("⚠️ Optimizer failed → equal-weight fallback.")
                return self._equal_weight_fallback(assets)

            return pd.DataFrame({
                "symbol": assets,
                "weight": w.value
            })

        except Exception as e:
            print(f"⚠️ Optimizer error → equal-weight fallback. Error: {e}")
            return self._equal_weight_fallback(assets)
