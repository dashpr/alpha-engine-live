"""
Institutional Alpha Backtest Engine
-----------------------------------

Creates alpha signals from raw OHLCV dataframe.

Input DF columns:
    date, symbol, open, high, low, close, volume

Output DF columns:
    date, symbol, ret, weight, model, regime
"""

import pandas as pd
import numpy as np


class AlphaBacktestEngine:
    """
    Institutional alpha engine supporting:

    - momentum
    - mean_reversion
    - ml_factor (placeholder deterministic factor blend)
    """

    def __init__(self, model_name: str):
        self.model_name = model_name.lower()

        if self.model_name not in {"momentum", "mean_reversion", "ml_factor"}:
            raise ValueError(f"Unknown alpha model: {model_name}")

    # ------------------------------------------------------------------
    # PUBLIC RUN
    # ------------------------------------------------------------------
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        print(f"\n🧠 Running Alpha Model → {self.model_name}")

        df = df.copy()

        # --------------------------------------------------------------
        # 1️⃣ CREATE RETURNS (CRITICAL MISSING STEP)
        # --------------------------------------------------------------
        df["ret_1d"] = df.groupby("symbol")["close"].pct_change()

        # drop first NaNs safely
        df = df.dropna(subset=["ret_1d"])

        # --------------------------------------------------------------
        # 2️⃣ DETECT MARKET REGIME
        # --------------------------------------------------------------
        regime = self._detect_regime(df)

        # map regime back
        df = df.merge(regime, on="date", how="left")

        # --------------------------------------------------------------
        # 3️⃣ CREATE ALPHA SIGNAL
        # --------------------------------------------------------------
        df["alpha"] = self._create_alpha(df)

        # --------------------------------------------------------------
        # 4️⃣ CONVERT TO PORTFOLIO WEIGHTS (TOP-15 INSTITUTIONAL)
        # --------------------------------------------------------------
        df["rank"] = df.groupby("date")["alpha"].rank(ascending=False)

        df["weight"] = np.where(df["rank"] <= 15, 1 / 15, 0)

        # --------------------------------------------------------------
        # 5️⃣ FINAL RETURN COLUMN
        # --------------------------------------------------------------
        df["ret"] = df["ret_1d"] * df["weight"]

        # --------------------------------------------------------------
        # 6️⃣ OUTPUT STRUCTURE
        # --------------------------------------------------------------
        out = df[["date", "symbol", "ret", "weight", "regime"]].copy()
        out["model"] = self.model_name

        print(f"📈 Alpha rows: {len(out):,}")

        return out.sort_values(["date", "symbol"]).reset_index(drop=True)

    # ------------------------------------------------------------------
    # REGIME DETECTION (VOLATILITY BASED)
    # ------------------------------------------------------------------
    def _detect_regime(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Institutional simple regime:

        High volatility → RISK_OFF  
        Low volatility  → RISK_ON
        """

        vol = df.groupby("date")["ret_1d"].std()

        threshold = vol.rolling(252).mean()  # 1-year avg vol

        regime = pd.DataFrame({
            "date": vol.index,
            "regime": np.where(vol > threshold, "risk_off", "risk_on")
        })

        return regime

    # ------------------------------------------------------------------
    # ALPHA MODELS
    # ------------------------------------------------------------------
    def _create_alpha(self, df: pd.DataFrame) -> pd.Series:

        if self.model_name == "momentum":
            # 6-month momentum
            return df.groupby("symbol")["close"].pct_change(126)

        if self.model_name == "mean_reversion":
            # short-term reversal
            return -df.groupby("symbol")["close"].pct_change(5)

        if self.model_name == "ml_factor":
            # deterministic proxy for ML:
            # blend of momentum + reversal + volatility filter

            mom = df.groupby("symbol")["close"].pct_change(126)
            rev = -df.groupby("symbol")["close"].pct_change(5)
            vol = df.groupby("symbol")["ret_1d"].rolling(20).std().reset_index(level=0, drop=True)

            return 0.5 * mom + 0.3 * rev - 0.2 * vol

        raise ValueError("Invalid model")
