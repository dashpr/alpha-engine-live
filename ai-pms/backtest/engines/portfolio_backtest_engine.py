import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional Portfolio Backtest Engine
    --------------------------------------
    Converts equity curve → performance metrics.
    """

    def __init__(self, risk_free_rate: float = 0.05):
        self.risk_free_rate = risk_free_rate

    # --------------------------------------------------
    # Performance Metrics
    # --------------------------------------------------
    def compute_metrics(self, equity: pd.DataFrame) -> dict:
        """
        equity index: date
        equity column: equity
        """

        df = equity.copy()

        # Daily returns
        df["ret"] = df["equity"].pct_change().fillna(0)

        # CAGR
        total_years = (df.index[-1] - df.index[0]).days / 365
        if total_years <= 0:
            cagr = 0.0
        else:
            cagr = (df["equity"].iloc[-1] / df["equity"].iloc[0]) ** (1 / total_years) - 1

        # Volatility
        vol = df["ret"].std() * np.sqrt(252)

        # Sharpe Ratio
        sharpe = (
            (df["ret"].mean() * 252 - self.risk_free_rate) / vol
            if vol != 0
            else 0.0
        )

        # Max Drawdown
        running_max = df["equity"].cummax()
        drawdown = df["equity"] / running_max - 1
        max_dd = drawdown.min()

        return {
            "CAGR": float(cagr),
            "Volatility": float(vol),
            "Sharpe": float(sharpe),
            "MaxDrawdown": float(max_dd),
        }
