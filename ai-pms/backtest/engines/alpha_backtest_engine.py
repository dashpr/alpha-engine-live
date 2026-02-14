import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional Alpha Generator for Phase-5

    REQUIRED OUTPUT SCHEMA:
        date | ret | model | regime
    """

    def __init__(self, model_name: str = "momentum"):
        self.model_name = model_name

    # ---------------------------------------------------------
    # Regime detection (simple but deterministic)
    # ---------------------------------------------------------
    def _detect_regime(self, df: pd.DataFrame) -> pd.Series:
        """
        Simple volatility-based regime proxy.
        This keeps Phase-5 deterministic & reproducible.
        """

        vol = df.groupby("date")["ret_1d"].std()

        regime = pd.Series(index=vol.index, dtype="object")

        regime[vol < vol.quantile(0.33)] = "bull"
        regime[(vol >= vol.quantile(0.33)) & (vol <= vol.quantile(0.66))] = "sideways"
        regime[vol > vol.quantile(0.66)] = "bear"

        return regime

    # ---------------------------------------------------------
    # Alpha models
    # ---------------------------------------------------------
    def _momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["ret"] = (
            df.groupby("symbol")["close"]
            .pct_change(20)
        )

        return df

    def _mean_reversion(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        z = (
            df.groupby("symbol")["close"]
            .transform(lambda x: (x - x.rolling(20).mean()) / x.rolling(20).std())
        )

        df["ret"] = -z / 100  # scaled

        return df

    def _ml_factor(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Placeholder deterministic ML proxy.
        Real ML comes in Phase-6.
        """

        df = df.copy()

        mom = df.groupby("symbol")["close"].pct_change(60)
        vol = df.groupby("symbol")["close"].pct_change().rolling(20).std().reset_index(level=0, drop=True)

        score = mom - vol
        df["ret"] = score / 50

        return df

    # ---------------------------------------------------------
    # Dispatcher
    # ---------------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.DataFrame:

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

        df = df.sort_values(["symbol", "date"])

        # ---------------------------------------------
        # Create alpha returns
        # ---------------------------------------------
        df = self._create_alpha(df)

        # drop NaNs from rolling windows
        df = df.dropna(subset=["ret"])

        # ---------------------------------------------
        # Detect regime
        # ---------------------------------------------
        regime_series = self._detect_regime(df)

        df = df.merge(
            regime_series.rename("regime"),
            left_on="date",
            right_index=True,
            how="left",
        )

        # ---------------------------------------------
        # Final institutional schema
        # ---------------------------------------------
        out = df[["date", "ret", "regime"]].copy()
        out["model"] = self.model_name

        # enforce types
        out["ret"] = pd.to_numeric(out["ret"], errors="coerce")
        out = out.dropna()

        return out.reset_index(drop=True)
