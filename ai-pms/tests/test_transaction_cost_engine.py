import pandas as pd
from backtest.reality.transaction_cost_engine import TransactionCostEngine


def test_transaction_cost_engine_runs():
    engine = TransactionCostEngine()

    trades = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "symbol": ["A", "A"],
            "side": ["BUY", "SELL"],
            "value": [100000, 100000],
        }
    )

    trades_with_cost = engine.apply_costs(trades)

    assert "transaction_cost" in trades_with_cost.columns
    assert trades_with_cost["transaction_cost"].sum() > 0
