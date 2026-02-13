import pandas as pd
from pathlib import Path

from src.optimizer import PortfolioOptimizer
from src.risk_engine import RiskEngine

ALPHA_PATH = Path("data/output/alpha_scores.parquet")
FEATURE_PATH = Path("data/output/features.parquet")

WEIGHTS_OUT = Path("data/output/final_weights.parquet")
RISK_OUT = Path("data/output/risk_state.parquet")


def main():
    alpha = pd.read_parquet(ALPHA_PATH)
    features = pd.read_parquet(FEATURE_PATH)

    latest_alpha = alpha.sort_values("date").groupby("symbol").tail(1)

    returns = features[["date", "symbol", "ret_1d"]]
    pivot = returns.pivot(index="date", columns="symbol", values="ret_1d").dropna()

    cov = pivot.cov()

    optimizer = PortfolioOptimizer(max_weight=0.1)
    weights = optimizer.optimize(latest_alpha, cov)

    risk_engine = RiskEngine()
    risk_state = risk_engine.build_risk_state(weights, returns)

    WEIGHTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    weights.to_parquet(WEIGHTS_OUT, index=False)
    risk_state.to_parquet(RISK_OUT, index=False)

    print("✅ Portfolio Optimizer completed")
    print("✅ Risk Engine completed")


if __name__ == "__main__":
    main()
