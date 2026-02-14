"""
Alpha Backtest Engine — Phase-5 Institutional
Generates daily top-N alpha portfolio from historical dataframe.
"""

from typing import Optional
import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    def __init__(
        self,
        top_n: int = 20,
        rebalance_days: int = 5,
    ):
        """
        Parameters
        ----------
        top_n : int
            Number of stocks in portfolio

        rebalance_days : int
            Rebalance frequency in trading days
        """
        self.top_n = top_n
        self.rebalance_days = rebalance_days

    # -----------------------------------------------------

    def _create_simple_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Institutional placeholder alpha:
        Momentum over last 20 days.
        """

        df = df.copy()

        df["ret_20"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        return df

    # -----------------------------------------------------

    def _select_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Select top-N stocks by alpha each rebalance date.
        """

        df = df.dropna(subset=["ret_20"])

        if df.empty:
            raise ValueError("Alpha dataframe empty after feature creation")

        # rebalance dates
        unique_dates = sorted(df["date"].unique())
        rebalance_dates = unique_dates[:: self.rebalance_days]

        portfolios = []

        for d in rebalance_dates:
            day_df = df[df["date"] == d]

            top = (
                day_df.sort_values("ret_20", ascending=False)
                .head(self.top_n)
                .assign(weight=1 / self.top_n)
            )

            portfolios.append(top)

        return pd.concat(portfolios, ignore_index=True)

    # -----------------------------------------------------

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main execution.
        """

        if df.empty:
            raise ValueError("Historical dataframe is empty")

        df = self._create_simple_alpha(df)
        portfolio = self._select_portfolio(df)

        print("\n📈 Alpha Portfolio Generated")
        print(f"Rows : {len(portfolio):,}")
        print(f"Dates: {portfolio['date'].nunique()}")

        return portfolio
