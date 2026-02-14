"""
Phase-4.5 Reality Layer
Institutional Stress Test Engine — FINAL STABLE
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class StressTestEngine:
    """
    Simulates extreme but realistic market regimes
    on an existing equity curve.
    """

    # --------------------------------------------------

    def _to_float(self, equity: pd.Series) -> pd.Series:
        """
        Ensure equity is float for safe arithmetic.
        """
        return equity.astype(float)

    # --------------------------------------------------

    def crash_shock(self, equity: pd.Series) -> pd.Series:
        """
        Instant −25% shock after a few periods.
        """
        shocked = self._to_float(equity.copy())

        if len(shocked) > 5:
            shocked.iloc[5:] = shocked.iloc[5:] * 0.75

        return shocked

    # --------------------------------------------------

    def volatility_storm(self, equity: pd.Series) -> pd.Series:
        """
        High-variance sideways noise.
        """
        equity = self._to_float(equity)

        noise = np.random.normal(0, 0.03, size=len(equity))
        path = (1 + noise).cumprod()

        return equity * path / path[0]

    # --------------------------------------------------

    def prolonged_bear(self, equity: pd.Series) -> pd.Series:
        """
        Gradual −40% decline.
        """
        equity = self._to_float(equity)

        trend = np.linspace(1.0, 0.6, len(equity))
        return equity * trend

    # --------------------------------------------------

    def run_all(self, equity_curve: pd.DataFrame) -> pd.DataFrame:
        """
        Returns stress-tested equity curves.
        """

        if equity_curve.empty:
            return equity_curve

        if "equity" not in equity_curve.columns:
            raise ValueError("equity column required")

        base = self._to_float(equity_curve["equity"])

        out = pd.DataFrame(
            {
                "date": equity_curve.get("date", pd.RangeIndex(len(base))),
                "base": base,
                "crash": self.crash_shock(base),
                "vol_storm": self.volatility_storm(base),
                "bear": self.prolonged_bear(base),
            }
        )

        return out
