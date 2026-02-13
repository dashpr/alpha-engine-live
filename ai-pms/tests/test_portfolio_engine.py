import pandas as pd
import numpy as np

from src.optimizer import PortfolioOptimizer


def test_optimizer_runs():
    alpha = pd.DataFrame({
        "symbol": ["A", "B", "C"],
        "alpha_score": [0.05, 0.02, 0.01],
    })

    cov = pd.DataFrame(
        np.eye(3),
        columns=["A", "B", "C"],
        index=["A", "B", "C"],
    )

    opt = PortfolioOptimizer(max_weight=0.5)
    w = opt.optimize(alpha, cov)

    assert abs(w["weight"].sum() - 1) < 1e-6
