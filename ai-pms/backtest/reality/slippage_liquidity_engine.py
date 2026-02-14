"""
Phase-4.5 Reality Layer
Slippage & Liquidity Participation Engine
"""

from __future__ import annotations

import pandas as pd


class SlippageLiquidityEngine:
    """
    Simulates execution realism using:

    • ADV participation cap
    • Size-based slippage
    """

    # Institutional assumptions (India mid-liquidity universe)
    MAX_ADV_PARTICIPATION = 0.10   # 10% of ADV
    BASE_SLIPPAGE = 0.0005         # 0.05%

    # --------------------------------------------------

    def apply_liquidity_constraints(self, trades: pd.DataFrame) -> pd.DataFrame:
        """
        trades must contain:
        date | symbol | side | value | adv
        """

        if trades.empty:
            return trades

        trades = trades.copy()

        # Max tradable value per day
        trades["max_trade_value"] = trades["adv"] * self.MAX_ADV_PARTICIPATION

        # Flag trades exceeding liquidity
        trades["liquidity_breach"] = trades["value"] > trades["max_trade_value"]

        # Clip trade value to allowed liquidity
        trades["executed_value"] = trades[["value", "max_trade_value"]].min(axis=1)

        return trades

    # --------------------------------------------------

    def apply_slippage(self, trades: pd.DataFrame) -> pd.DataFrame:
        """
        Adds size-based slippage cost.
        """

        if trades.empty:
            return trades

        trades = trades.copy()

        # Size-scaled slippage
        trades["slippage_pct"] = self.BASE_SLIPPAGE * (
            trades["executed_value"] / trades["adv"]
        ).clip(upper=1)

        trades["slippage_cost"] = trades["executed_value"] * trades["slippage_pct"]

        return trades
