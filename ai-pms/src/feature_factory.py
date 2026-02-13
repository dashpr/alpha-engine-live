import pandas as pd

from .config import ROLLING_WINDOWS, VOL_WINDOWS


class FeatureFactory:

    def __init__(self, price_df: pd.DataFrame):
        self.df = price_df.copy()

    def _returns(self):
        for w in [1] + ROLLING_WINDOWS:
            self.df[f"ret_{w}d"] = (
                self.df.groupby("symbol")["close"].pct_change(w)
            )

    def _volatility(self):
        for w in VOL_WINDOWS:
            self.df[f"vol_{w}d"] = (
                self.df.groupby("symbol")["ret_1d"]
                .rolling(w)
                .std()
                .reset_index(level=0, drop=True)
            )

    def _drawdown(self):
        rolling_max = (
            self.df.groupby("symbol")["close"]
            .cummax()
        )
        self.df["drawdown"] = self.df["close"] / rolling_max - 1

    def _momentum(self):
        self.df["mom_20_60"] = (
            self.df["ret_20d"] - self.df["ret_60d"]
        )

        for ma in [50, 200]:
            ma_series = (
                self.df.groupby("symbol")["close"]
                .rolling(ma)
                .mean()
                .reset_index(level=0, drop=True)
            )
            self.df[f"price_vs_ma{ma}"] = self.df["close"] / ma_series - 1

    def _cross_sectional_ranks(self):
        rank_cols = ["ret_20d", "mom_20_60", "vol_20d"]

        for col in rank_cols:
            self.df[f"rank_{col}"] = (
                self.df.groupby("date")[col]
                .rank(pct=True)
            )

    def build_features(self) -> pd.DataFrame:
        self._returns()
        self._volatility()
        self._drawdown()
        self._momentum()
        self._cross_sectional_ranks()

        return self.df.dropna().reset_index(drop=True)
