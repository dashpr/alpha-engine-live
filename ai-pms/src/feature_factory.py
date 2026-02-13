import pandas as pd
import numpy as np


class FeatureFactory:
    def __init__(self, df: pd.DataFrame):
        self.df = df.sort_values(["symbol", "date"]).copy()

    def build_features(self) -> pd.DataFrame:
        df = self.df.copy()

        df["ret_1d"] = df.groupby("symbol")["close"].pct_change()
        df["ret_5d"] = df.groupby("symbol")["close"].pct_change(5)
        df["ret_20d"] = df.groupby("symbol")["close"].pct_change(20)
        df["ret_60d"] = df.groupby("symbol")["close"].pct_change(60)

        df["vol_20d"] = df.groupby("symbol")["ret_1d"].rolling(20).std().reset_index(0, drop=True)
        df["vol_60d"] = df.groupby("symbol")["ret_1d"].rolling(60).std().reset_index(0, drop=True)

        df["drawdown"] = df["close"] / df.groupby("symbol")["close"].cummax() - 1

        df["mom_20_60"] = df["ret_20d"] - df["ret_60d"]

        # ⭐ key fix → allow small datasets
        df = df.fillna(0)

        return df
