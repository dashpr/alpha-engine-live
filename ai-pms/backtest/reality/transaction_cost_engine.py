"""
Phase-4.5 Reality Layer
Transaction Cost Engine — India Flat Model
"""

from __future__ import annotations

import pandas as pd


class TransactionCostEngine:
    """
    Applies realistic Indian equity delivery costs to backtest trades.
    """

    # Flat % costs
    BUY_COST = 0.00083   # 0.083%
    SELL_COST = 0.00183  # 0.183%

    def apply_costs(self, trades: pd.DataFrame) -> pd.DataFrame:
        """
        trades must contain:
        date | symbol | side (BUY/SELL) | value
        """

        if trades.empty:
            return trades

        trades = trades.copy()

        def _cost(row):
            if row["side"] == "BUY":
                return row["value"] * self.BUY_COST
            return row["value"] * self.SELL_COST

        trades["transaction_cost"] = trades.apply(_cost, axis=1)

        return trades

    # --------------------------------------------------

    def net_returns(self, equity_curve: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
        """
        Deduct cumulative transaction costs from equity curve.
        """

        if equity_curve.empty:
            return equity_curve

        total_cost = trades["transaction_cost"].sum() if not trades.empty else 0

        equity_curve = equity_curve.copy()
        equity_curve["net_equity"] = equity_curve["equity"] - total_cost

        return equity_curve
