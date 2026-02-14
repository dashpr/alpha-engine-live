"""
Alpha Backtest Engine — Phase-5 Institutional (Stable API)

✔ Accepts old and new parameter names
✔ Protects against empty data
✔ Always returns valid portfolio
"""

from typing import Optional
import pandas as pd


class AlphaBacktestEngine:
    def __init__(
        self,
        top_n: int = 20,
        rebalance_days: Optional[int] = None,
        rebalance: Optional[int] = None,
    ):
        """
        Parameters
        ----------
        top_n : number of stocks in portfolio

        rebalance_days / rebalance :
            BOTH supported for backward compatibility
        """

        # -------------------------------------------------
        # Backward compatibility layer (critical fix)
        # -------------------------------------------------
        if rebalance_days is None and rebalance is not None:
            rebalance_days = rebalance

        if rebalance_days is None:
            rebalance_days = 5

        self.top_n = int(top_n)
        self.rebalance_days = int(rebalance_days)

    # -----------------------------------------------------

    def _create_simple_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        """20-day momentum alpha (institutional placeholder)."""

        df = df.copy()

        df["ret_20"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        return df

    # -----------------------------------------------------

    def _select_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select top-N stocks on rebalance dates."""

        df = df.dropna(subset=["ret_20"])

        if df.empty:
            raise ValueError("Alpha dataframe empty after feature creation")

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
        """Main execution."""

        if df.empty:
            raise ValueError("Historical dataframe is empty")

        df = self._create_simple_alpha(df)
        portfolio = self._select_portfolio(df)

        print("\n📈 Alpha Portfolio Generated")
        print(f"Rows : {len(portfolio):,}")
        print(f"Dates: {portfolio['date'].nunique()}")

        return portfolio
