import pandas as pd
from pathlib import Path

from src.regime_model import RegimeDetector
from src.config import OUTPUT_FEATURE_FILE

OUTPUT_REGIME_FILE = Path("data/output/regime_state.parquet")


def main():
    df = pd.read_parquet(OUTPUT_FEATURE_FILE)

    detector = RegimeDetector(n_states=3)
    detector.fit(df)

    daily_probs = detector.predict_daily_probabilities(df)
    weekly_regime = detector.weekly_confirmed_regime(daily_probs)

    OUTPUT_REGIME_FILE.parent.mkdir(parents=True, exist_ok=True)
    weekly_regime.to_parquet(OUTPUT_REGIME_FILE, index=False)

    print("✅ Regime Detection completed")
    print(f"Output saved to: {OUTPUT_REGIME_FILE}")


if __name__ == "__main__":
    main()
