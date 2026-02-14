"""
Phase-4.5 Reality Layer
Drawdown-Aware Capital Scaling Engine
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class DrawdownScaler:
    """
    Adjusts portfolio exposure based on running drawdown.
    """

    # Institutional drawdown ladder
    DD_LEVEL_1 = -0.05   # -5%
    DD_LEVEL_2 = -0.08   # -8%
    DD_LEVEL_3 = -0.12   # -12%

    EXPOSURE_1 = 0.75
    EXPOSURE_2 = 0.50
    EXPOSURE_3 = 0.20

    # --------------------------------------------------

    def compute_drawdown(self, equity_curve: pd.Series) -> pd.Series:
        """
        Running drawdown series.
        """
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak
        return drawdown

    # --------------------------------------------------

    def exposure_from_drawdown(self, drawdown: float) -> float:
        """
        Map drawdown → exposure multiplier.
        """

        if drawdown <= self.DD_LEVEL_3:
            return self.EXPOSURE_3
        if drawdown <= self.DD_LEVEL_2:
            return self.EXPOSURE_2
        if drawdown <= self.DD_LEVEL_1:
            return self.EXPOSURE_1
        return 1.0

    # --------------------------------------------------

    def apply_scaling(self, equity_curve: pd.DataFrame) -> pd.DataFrame:
        """
        Adds:
        • drawdown
        • exposure multiplier
        • scaled equity curve
        """

        if equity_curve.empty:
            return equity_curve

        df = equity_curve.copy()

        if "equity" not in df.columns:
            raise ValueError("equity column required")

        df["drawdown"] = self.compute_drawdown(df["equity"])

        df["exposure"] = df["drawdown"].apply(self.exposure_from_drawdown)

        # scaled equity assumes proportional capital deployment
        df["scaled_equity"] = df["equity"] * df["exposure"]

        return df
