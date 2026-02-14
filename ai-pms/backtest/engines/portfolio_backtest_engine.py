"""
Institutional Portfolio Backtest Engine
Converts alpha signals → equity curve → performance metrics.
"""

import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Runs portfolio simulation on alpha dataframe.
    """

    def __init__(self, initial_capital: float = 100_000):
        self.initial_capital = initial_capital

    # -----------------------------------------------------
    # Build equity curve
    # -----------------------------------------------------
    def _build_equity_curve(self, df: pd.DataFrame) -> pd.Series:
        """
        Assumes df has:
        date | symbol | ret | weight
        """

        df = df.copy()
        df["weighted_ret"] = df["ret"] * df["weight"]

        daily_ret = df.groupby("date")["weighted_ret"].sum()

        equity = (1 + daily_ret).cumprod() * self.initial_capital

        return equity

    # -----------------------------------------------------
    # Compute metrics
    # -----------------------------------------------------
    def _compute_metrics(self, equity: pd.Series) -> dict:
        returns = equity.pct_change().dropna()

        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(equity)) - 1

        max_dd = ((equity / equity.cummax()) - 1).min()

        sharpe = np.sqrt(252) * returns.mean() / returns.std() if returns.std() != 0 else 0

        return {
            "CAGR": round(float(cagr), 4),
            "Max Drawdown": round(float(max_dd), 4),
            "Sharpe": round(float(sharpe), 3),
        }

    # -----------------------------------------------------
    # PUBLIC RUN METHOD  ← CRITICAL STANDARDIZATION
    # -----------------------------------------------------
    def run(self, alpha_df: pd.DataFrame) -> dict:
        """
        Main institutional entrypoint.
        """

        if alpha_df.empty:
            raise ValueError("Alpha dataframe is empty")

        required_cols = {"date", "ret", "weight"}
        if not required_cols.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required_cols}")

        equity = self._build_equity_curve(alpha_df)

        metrics = self._compute_metrics(equity)

        print("\n📊 Portfolio Backtest Complete")
        for k, v in metrics.items():
            print(f"{k}: {v}")

        return metrics
