import pandas as pd


class AlphaBacktestEngine:
    """
    Institutional Alpha Construction Engine
    ---------------------------------------
    Outputs tradable portfolio frame with:

        date
        symbol
        weight
        ret   (forward return until next rebalance)

    Weekly rebalance baseline.
    """

    def __init__(self, top_n: int = 20, rebalance_days: int = 5):
        self.top_n = top_n
        self.rebalance_days = rebalance_days

    # ---------------------------------------------------------
    # Create simple momentum alpha
    # ---------------------------------------------------------
    def _create_simple_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(["symbol", "date"]).copy()

        # ensure numeric close
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        # 20-day momentum
        df["mom_20"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        return df

    # ---------------------------------------------------------
    # Select weekly top-N portfolio
    # ---------------------------------------------------------
    def _select_portfolio(self, df: pd.DataFrame) -> pd.DataFrame:
        # weekly rebalance dates
        rebalance_dates = (
            df["date"]
            .drop_duplicates()
            .sort_values()
            .iloc[:: self.rebalance_days]
        )

        portfolio_rows = []

        for dt in rebalance_dates:
            snap = df[df["date"] == dt].dropna(subset=["mom_20"])

            if snap.empty:
                continue

            top = snap.nlargest(self.top_n, "mom_20").copy()

            # equal weight
            top["weight"] = 1.0 / len(top)

            portfolio_rows.append(top[["date", "symbol", "weight"]])

        return pd.concat(portfolio_rows, ignore_index=True)

    # ---------------------------------------------------------
    # Compute forward returns
    # ---------------------------------------------------------
    def _add_forward_returns(self, df: pd.DataFrame, portfolio: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(["symbol", "date"])

        # forward return over rebalance window
        df["fwd_ret"] = (
            df.groupby("symbol")["close"]
            .shift(-self.rebalance_days)
            / df["close"]
            - 1
        )

        merged = portfolio.merge(
            df[["date", "symbol", "fwd_ret"]],
            on=["date", "symbol"],
            how="left",
        )

        merged = merged.rename(columns={"fwd_ret": "ret"})

        return merged.dropna(subset=["ret"])

    # ---------------------------------------------------------
    # PUBLIC RUN
    # ---------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise ValueError("Historical dataframe is empty")

        df = self._create_simple_alpha(df)

        portfolio = self._select_portfolio(df)

        portfolio = self._add_forward_returns(df, portfolio)

        return portfolio
