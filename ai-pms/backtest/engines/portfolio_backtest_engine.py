import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional Portfolio Backtest Engine

    Supports:
    - Brokerage
    - Slippage
    - Market impact
    - Cash drag
    - Equity curve
    - CAGR / Sharpe / Max Drawdown
    """

    def __init__(
        self,
        brokerage: float = 0.0005,   # 5 bps
        slippage: float = 0.0007,    # 7 bps
        impact: float = 0.0003,      # 3 bps
        cash_drag: float = 0.0002,   # 2 bps idle cash cost
    ):
        # Total institutional cost per rebalance day
        self.total_cost = brokerage + slippage + impact + cash_drag

    # -------------------------------------------------------------
    # Build equity curve
    # -------------------------------------------------------------
    def _build_equity_curve(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        required_cols = {"date", "weight", "ret"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required_cols}")

        # Daily portfolio return
        portfolio_ret = (
            df.groupby("date")
            .apply(lambda x: np.sum(x["weight"] * x["ret"]))
            .sort_index()
        )

        # Subtract institutional costs
        portfolio_ret = portfolio_ret - self.total_cost

        # Equity curve
        equity = (1 + portfolio_ret).cumprod()

        return pd.DataFrame({
            "date": portfolio_ret.index,
            "ret": portfolio_ret.values,
            "equity": equity.values,
        })

    # -------------------------------------------------------------
    # Performance metrics
    # -------------------------------------------------------------
    def _compute_metrics(self, equity_df: pd.DataFrame) -> dict:
        ret = equity_df["ret"]

        total_return = equity_df["equity"].iloc[-1] - 1
        years = len(equity_df) / 252

        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        sharpe = (
            np.sqrt(252) * ret.mean() / ret.std()
            if ret.std() > 0 else 0
        )

        drawdown = equity_df["equity"] / equity_df["equity"].cummax() - 1
        max_dd = drawdown.min()

        return {
            "CAGR": round(cagr * 100, 2),
            "Sharpe": round(sharpe, 2),
            "MaxDD": round(max_dd * 100, 2),
        }

    # -------------------------------------------------------------
    # Public runner
    # -------------------------------------------------------------
    def run(self, alpha_df: pd.DataFrame) -> dict:
        equity_df = self._build_equity_curve(alpha_df)
        metrics = self._compute_metrics(equity_df)
        return metrics
