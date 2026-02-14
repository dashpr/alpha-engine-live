import pandas as pd
from backtest.reality.slippage_liquidity_engine import SlippageLiquidityEngine


def test_slippage_liquidity_engine_runs():
    engine = SlippageLiquidityEngine()

    trades = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "symbol": ["A"],
            "side": ["BUY"],
            "value": [100000],
            "adv": [1000000],
        }
    )

    trades = engine.apply_liquidity_constraints(trades)
    trades = engine.apply_slippage(trades)

    assert "executed_value" in trades.columns
    assert "slippage_cost" in trades.columns
    assert trades["executed_value"].iloc[0] <= trades["value"].iloc[0]
