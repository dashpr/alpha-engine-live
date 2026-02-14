import pandas as pd
from backtest.reality.turnover_governor import TurnoverGovernor


def test_turnover_governor_runs():
    gov = TurnoverGovernor()

    prev = pd.Series({"A": 0.5, "B": 0.5})
    new = pd.Series({"A": 0.9, "B": 0.1})

    new_adj = gov.apply_threshold(prev, new)
    capped = gov.enforce_turnover_cap(prev, new_adj)

    assert isinstance(capped, pd.Series)
    assert abs(capped.sum() - 1) < 1e-6
