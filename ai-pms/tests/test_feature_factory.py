import pandas as pd
from src.feature_factory import FeatureFactory


def test_feature_generation():
    data = {
        "symbol": ["A", "A", "A", "A", "A", "A"],
        "date": pd.date_range("2024-01-01", periods=6),
        "close": [100, 101, 102, 103, 104, 105],
    }

    df = pd.DataFrame(data)

    factory = FeatureFactory(df)
    features = factory.build_features()

    assert not features.empty
    assert "ret_1d" in features.columns
