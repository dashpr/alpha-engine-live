import pandas as pd
from pathlib import Path

from src.alpha_model import AlphaModel
from src.config import OUTPUT_FEATURE_FILE

MODEL_PATH = Path("data/output/alpha_model.pkl")
ALPHA_OUTPUT = Path("data/output/alpha_scores.parquet")


def main():
    df = pd.read_parquet(OUTPUT_FEATURE_FILE)

    model = AlphaModel()
    model.fit(df)

    scores = model.predict(df.dropna())

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)

    scores.to_parquet(ALPHA_OUTPUT, index=False)

    print("✅ Alpha Engine completed")
    print(f"Alpha scores saved to: {ALPHA_OUTPUT}")


if __name__ == "__main__":
    main()
