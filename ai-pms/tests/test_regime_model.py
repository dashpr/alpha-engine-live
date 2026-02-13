import pandas as pd
import numpy as np

from src.regime_model import RegimeDetector


def test_regime_detection_runs():
    dates = pd.date_range("2024-01-01", periods=200)

    df = pd.DataFrame(
        {
            "date": dates,
            "ret_1d": np.random.randn(200) * 0.01,
            "vol_20d": np.random.rand(200) * 0.02,
            "mom_20_60": np.random.randn(200) * 0.05,
        }
    )

    detector = RegimeDetector(n_states=3)
    detector.fit(df)

    probs = detector.predict_daily_probabilities(df)
    weekly = detector.weekly_confirmed_regime(probs)

    assert not weekly.empty
    assert "confirmed_regime" in weekly.columns
