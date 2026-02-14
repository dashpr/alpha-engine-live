import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Generates alpha signals for:
    - momentum
    - mean_reversion
    - ml_factor (proxy factor blend)
    """

    def __init__(self, model_name: str):
        self.model_name = model_name

    # -----------------------------------------------------
    def _detect_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Simple volatility regime:
        High vol if cross-sectional std of daily returns above rolling median.
        """
        vol = df.groupby("date")["ret_1d"].std()
        threshold = vol.rolling(60).median()

        regime = (vol > threshold).astype(int)
        regime.name = "regime"

        return regime

    # -----------------------------------------------------
    def _momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df["score"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )
        return df

    # -----------------------------------------------------
    def _mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df["score"] = -df.groupby("symbol")["close"].pct_change(5)
        return df

    # -----------------------------------------------------
    def _ml_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Proxy ML factor:
        blend of momentum, reversal, and volatility normalization.
        """
        mom = df.groupby("symbol")["close"].pct_change(20)
        rev = -df.groupby("symbol")["close"].pct_change(5)
        vol = df.groupby("symbol")["ret_1d"].rolling(20).std().reset_index(level=0, drop=True)

        df["score"] = (mom + rev) / (vol + 1e-6)
        return df

    # -----------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.model_name == "momentum":
            df = self._momentum(df)
        elif self.model_name == "mean_reversion":
            df = self._mean_reversion(df)
        elif self.model_name == "ml_factor":
            df = self._ml_factor(df)
        else:
            raise ValueError(f"Unknown alpha model: {self.model_name}")

        return df

    # -----------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n🧠 Running Alpha Model → {self.model_name}")

        df = df.copy()
        df = self._create_alpha(df)

        regime = self._detect_regime(df)
        df = df.merge(regime, on="date", how="left")

        df = df.dropna(subset=["score", "ret_1d"])

        # weekly rebalance snapshot
        df["week"] = df["date"].dt.to_period("W").dt.start_time
        df = df.sort_values(["date", "score"], ascending=[True, False])

        # top-15
        df["rank"] = df.groupby("week")["score"].rank(ascending=False, method="first")
        df = df[df["rank"] <= 15]

        df["model"] = self.model_name
        df = df.rename(columns={"ret_1d": "ret"})

        print(f"📈 Alpha rows: {len(df):,}")

        return df[["date", "symbol", "ret", "score", "regime", "model"]]
