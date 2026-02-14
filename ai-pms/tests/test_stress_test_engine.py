import pandas as pd
from backtest.reality.stress_test_engine import StressTestEngine


def test_stress_engine_runs():
    engine = StressTestEngine()

    equity = pd.DataFrame(
        {"equity": [100, 102, 105, 103, 101, 99, 98, 97]}
    )

    out = engine.run_all(equity)

    assert "crash" in out.columns
    assert "vol_storm" in out.columns
    assert "bear" in out.columns
