import pandas as pd
from backtest.reality.drawdown_scaler import DrawdownScaler


def test_drawdown_scaler_runs():
    scaler = DrawdownScaler()

    equity = pd.DataFrame(
        {
            "equity": [100, 105, 102, 95, 90, 92]
        }
    )

    out = scaler.apply_scaling(equity)

    assert "drawdown" in out.columns
    assert "exposure" in out.columns
    assert "scaled_equity" in out.columns
