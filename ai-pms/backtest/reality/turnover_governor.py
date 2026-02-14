"""
Phase-4.5 Reality Layer
Turnover Governor Engine
"""

from __future__ import annotations

import pandas as pd
import numpy as np


class TurnoverGovernor:
    """
    Controls portfolio turnover using:

    • Weekly turnover cap
    • Minimum rebalance threshold
    """

    MAX_WEEKLY_TURNOVER = 0.30   # 30%
    MIN_WEIGHT_CHANGE = 0.01     # 1%

    # --------------------------------------------------

    def compute_turnover(
        self,
        prev_weights: pd.Series,
        new_weights: pd.Series,
    ) -> float:
        """
        L1 turnover between two portfolios.
        """

        all_symbols = prev_weights.index.union(new_weights.index)

        prev = prev_weights.reindex(all_symbols).fillna(0)
        new = new_weights.reindex(all_symbols).fillna(0)

        turnover = np.abs(new - prev).sum() / 2
        return float(turnover)

    # --------------------------------------------------

    def apply_threshold(
        self,
        prev_weights: pd.Series,
        new_weights: pd.Series,
    ) -> pd.Series:
        """
        Ignore tiny changes that create unnecessary trades.
        """

        adjusted = new_weights.copy()

        for sym in adjusted.index:
            prev_w = prev_weights.get(sym, 0)
            if abs(adjusted[sym] - prev_w) < self.MIN_WEIGHT_CHANGE:
                adjusted[sym] = prev_w

        # renormalize
        total = adjusted.sum()
        if total > 0:
            adjusted /= total

        return adjusted

    # --------------------------------------------------

    def enforce_turnover_cap(
        self,
        prev_weights: pd.Series,
        new_weights: pd.Series,
    ) -> pd.Series:
        """
        Scale trades down if turnover exceeds cap.
        """

        turnover = self.compute_turnover(prev_weights, new_weights)

        if turnover <= self.MAX_WEEKLY_TURNOVER:
            return new_weights

        scale = self.MAX_WEEKLY_TURNOVER / turnover

        adjusted = prev_weights + (new_weights - prev_weights) * scale

        # renormalize
        total = adjusted.sum()
        if total > 0:
            adjusted /= total

        return adjusted
