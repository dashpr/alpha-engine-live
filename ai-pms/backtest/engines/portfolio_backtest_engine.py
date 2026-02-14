import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    """
    Institutional weekly-rebalance portfolio simulator.
    Returns full equity curve for metrics computation.
    """

    def __init__(
        self,
        initial_capital: float = 100_000,
        transaction_cost: float = 0.0015,   # 15 bps realistic India
        rebalance_days: int = 5,            # weekly
    ):
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.rebalance_days = rebalance_days

    # ==========================================================
    def _prepare_returns(self, alpha_df: pd.DataFrame):
        """
        Expect columns:
        date | symbol | weight | ret
        """
        required = {"date", "symbol", "weight", "ret"}
        if not required.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required}")

        df = alpha_df.copy()
        df = df.sort_values(["date", "symbol"])

        # portfolio daily return = sum(weight * ret)
        port_ret = (
            df.groupby("date")
            .apply(lambda x: np.sum(x["weight"] * x["ret"]))
            .rename("ret")
            .reset_index()
        )

        return port_ret

    # ==========================================================
    def run(self, alpha_df: pd.DataFrame):
        """
        Returns:
        date | equity | ret
        """
        port_ret = self._prepare_returns(alpha_df)

        # apply transaction cost on rebalance days
        port_ret["cost"] = 0.0
        port_ret.loc[:: self.rebalance_days, "cost"] = self.transaction_cost

        port_ret["net_ret"] = port_ret["ret"] - port_ret["cost"]

        # equity curve
        port_ret["equity"] = self.initial_capital * (1 + port_ret["net_ret"]).cumprod()

        return port_ret[["date", "equity", "net_ret"]]
