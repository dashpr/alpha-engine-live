# ai-pms/backtest/engines/alpha_backtest_engine.py

import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    def __init__(self, model_name: str, rebalance_days: int = 5, top_n: int = 20):
        self.model_name = model_name
        self.rebalance_days = rebalance_days
        self.top_n = top_n

    # ---------- ALPHA MODELS ----------

    def _momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ret_20"] = df.groupby("symbol")["close"].pct_change(20)
        return df

    def _mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ret_5"] = df.groupby("symbol")["close"].pct_change(5)
        df["ret_20"] = df.groupby("symbol")["close"].pct_change(20)
        df["score"] = -df["ret_5"] + df["ret_20"]
        return df

    def _ml_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        df["mom"] = df.groupby("symbol")["close"].pct_change(20)
        df["vol"] = (
            df.groupby("symbol")["close"]
            .pct_change()
            .rolling(20)
            .std()
            .reset_index(level=0, drop=True)
        )
        df["score"] = df["mom"] / (df["vol"] + 1e-6)
        return df

    # ---------- SELECT MODEL ----------

    def _create_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model_name == "momentum":
            df = self._momentum(df)
            df["score"] = df["ret_20"]

        elif self.model_name == "mean_reversion":
            df = self._mean_reversion(df)

        elif self.model_name == "ml_factor":
            df = self._ml_factor(df)

        else:
            raise ValueError(f"Unknown alpha model: {self.model_name}")

        return df

    # ---------- PORTFOLIO SELECTION ----------

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self._create_alpha(df)
        df = df.dropna(subset=["score"])

        rebalance_dates = df["date"].drop_duplicates().sort_values()[:: self.rebalance_days]

        portfolio_rows = []

        for d in rebalance_dates:
            day_df = df[df["date"] == d].nlargest(self.top_n, "score")

            if day_df.empty:
                continue

            weight = 1.0 / len(day_df)

            for _, r in day_df.iterrows():
                portfolio_rows.append(
                    {
                        "date": d,
                        "symbol": r["symbol"],
                        "weight": weight,
                        "ret": 0.0,  # filled later
                    }
                )

        alpha_df = pd.DataFrame(portfolio_rows)

        # attach next-period return
        price = df[["date", "symbol", "close"]].copy()
        price["fwd_ret"] = price.groupby("symbol")["close"].pct_change().shift(-1)

        alpha_df = alpha_df.merge(price[["date", "symbol", "fwd_ret"]], on=["date", "symbol"], how="left")
        alpha_df["ret"] = alpha_df["fwd_ret"] * alpha_df["weight"]

        return alpha_df.dropna(subset=["ret"])
