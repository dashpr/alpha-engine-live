# ai-pms/backtest/engines/portfolio_backtest_engine.py

import pandas as pd
import numpy as np


class PortfolioBacktestEngine:
    def __init__(
        self,
        initial_capital: float = 200000,
        brokerage: float = 0.0005,
        slippage: float = 0.0005,
        cash_drag: float = 0.02,
    ):
        self.initial_capital = initial_capital
        self.brokerage = brokerage
        self.slippage = slippage
        self.cash_drag = cash_drag

    def run(self, alpha_df: pd.DataFrame) -> pd.DataFrame:
        required = {"date", "ret"}
        if not required.issubset(alpha_df.columns):
            raise ValueError(f"Alpha DF must contain columns: {required}")

        daily_ret = alpha_df.groupby("date")["ret"].sum()

        cost = self.brokerage + self.slippage
        daily_ret = daily_ret - cost / 5  # weekly cost spread

        equity = (1 + daily_ret).cumprod() * self.initial_capital

        return pd.DataFrame({"date": daily_ret.index, "equity": equity}).reset_index(drop=True)
