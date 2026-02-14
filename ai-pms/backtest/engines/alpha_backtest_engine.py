import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional Alpha Generator (Phase-5)

    INPUT REQUIRED:
        date | symbol | close

    OUTPUT GUARANTEED:
        date | ret | model | regime
    """

    # ---------------------------------------------------------
    def __init__(self, model_name: str = "momentum"):
        self.model_name = model_name

    # ---------------------------------------------------------
    # Internal data preparation (STRICT)
    # ---------------------------------------------------------
    def _prepare_base(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {"date", "symbol", "close"}

        if not required.issubset(df.columns):
            raise ValueError(f"Input DF must contain columns: {required}")

        df = df.copy()

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        df = df.dropna(subset=["date", "symbol", "close"])
        df = df.sort_values(["symbol", "date"])

        # ---- compute 1-day return internally (CRITICAL FIX)
        df["ret_1d"] = df.groupby("symbol")["close"].pct_change(1)

        return df

    # ---------------------------------------------------------
    # Regime detection (market volatility dispersion)
    # ---------------------------------------------------------
    def _detect_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Deterministic volatility regime.
        Uses cross-sectional std of daily returns.
        """

        market_vol = df.groupby("date")["ret_1d"].std()

        regime = pd.Series(index=market_vol.index, dtype="object")

        q1 = market_vol.quantile(0.33)
        q2 = market_vol.quantile(0.66)

        regime[market_vol <= q1] = "bull"
        regime[(market_vol > q1) & (market_vol <= q2)] = "sideways"
        regime[market_vol > q2] = "bear"

        return regime

    # ---------------------------------------------------------
    # Alpha models
    # ---------------------------------------------------------
    def _momentum(self, df: pd.DataFrame) -> pd.Series:
        return df.groupby("symbol")["close"].pct_change(20)

    def _mean_reversion(self, df: pd.DataFrame) -> pd.Series:
        z = df.groupby("symbol")["close"].transform(
            lambda x: (x - x.rolling(20).mean()) / x.rolling(20).std()
        )
        return -z / 100

    def _ml_factor(self, df: pd.DataFrame) -> pd.Series:
        """
        Deterministic ML proxy for Phase-5.
        Real ML enters Phase-6.
        """
        mom = df.groupby("symbol")["close"].pct_change(60)
        vol = (
            df.groupby("symbol")["close"]
            .pct_change()
            .rolling(20)
            .std()
            .reset_index(level=0, drop=True)
        )
        return (mom - vol) / 50

    # ---------------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.Series:

        if self.model_name == "momentum":
            return self._momentum(df)

        if self.model_name == "mean_reversion":
            return self._mean_reversion(df)

        if self.model_name == "ml_factor":
            return self._ml_factor(df)

        raise ValueError(f"Unknown alpha model: {self.model_name}")

    # ---------------------------------------------------------
    # PUBLIC RUN
    # ---------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:

        if df.empty:
            raise ValueError("Historical dataframe is empty")

        # ---- strict preparation
        df = self._prepare_base(df)

        # ---- alpha signal
        df["ret"] = self._create_alpha(df)

        df = df.dropna(subset=["ret"])

        # ---- regime detection
        regime_series = self._detect_regime(df)

        df = df.merge(
            regime_series.rename("regime"),
            left_on="date",
            right_index=True,
            how="left",
        )

        # ---- final institutional schema
        out = df[["date", "ret", "regime"]].copy()
        out["model"] = self.model_name

        out["ret"] = pd.to_numeric(out["ret"], errors="coerce")
        out = out.dropna()

        return out.reset_index(drop=True)
