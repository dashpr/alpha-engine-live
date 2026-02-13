import pandas as pd
import numpy as np

from src.alpha_model import AlphaModel


def test_alpha_model_runs():
    dates = pd.date_range("2024-01-01", periods=200)

    df = pd.DataFrame(
        {
            "date": dates.tolist() * 2,
            "symbol": ["A"] * 200 + ["B"] * 200,
            "ret_1d": np.random.randn(400) * 0.01,
            "ret_5d": np.random.randn(400) * 0.02,
            "ret_20d": np.random.randn(400) * 0.05,
            "ret_60d": np.random.randn(400) * 0.10,
            "vol_20d": np.random.rand(400) * 0.02,
            "mom_20_60": np.random.randn(400) * 0.05,
        }
    )

    model = AlphaModel()
    model.fit(df)

    preds = model.predict(df.dropna())

    assert not preds.empty
    assert "alpha_score" in preds.columns
