import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional weekly-rebalance long-only portfolio simulator
    Produces a clean equity curve required for CAGR computation.
    """

    def __init__(
        self,
        initial_capital: float = 100_000,
        transaction_cost: float = 0.001,   # 10 bps
        slippage: float = 0.0005,          # 5 bps
        rebalance_days: int = 5,           # weekly
    ):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.rebalance_days = rebalance_days

    # ---------------------------------------------------------
    # MAIN ENTRY
    # ---------------------------------------------------------
    def run(self, alpha_df: pd.DataFrame) -> pd.DataFrame:
        """
        Expected columns in alpha_df:
        date | symbol | weight | ret
        """

        required = {"date", "symbol", "weight", "ret"}
        if not required.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required}")

        df = alpha_df.copy()
        df = df.sort_values("date")

        # group daily portfolio return
        portfolio_returns = (
            df.groupby("date")
            .apply(lambda x: np.sum(x["weight"] * x["ret"]))
            .rename("gross_ret")
            .reset_index()
        )

        # -----------------------------------------------------
        # APPLY COSTS ON REBALANCE DAYS
        # -----------------------------------------------------
        portfolio_returns["cost"] = 0.0

        rebalance_idx = np.arange(0, len(portfolio_returns), self.rebalance_days)
        portfolio_returns.loc[rebalance_idx, "cost"] = (
            self.transaction_cost + self.slippage
        )

        portfolio_returns["net_ret"] = (
            portfolio_returns["gross_ret"] - portfolio_returns["cost"]
        )

        # -----------------------------------------------------
        # EQUITY CURVE
        # -----------------------------------------------------
        equity = [self.initial_capital]

        for r in portfolio_returns["net_ret"].iloc[1:]:
            equity.append(equity[-1] * (1 + r))

        portfolio_returns["equity"] = equity

        return portfolio_returns[["date", "equity", "net_ret"]]
