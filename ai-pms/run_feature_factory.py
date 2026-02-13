from src.utils import load_prices, save_parquet
from src.feature_factory import FeatureFactory
from src.config import INPUT_PRICE_FILE, OUTPUT_FEATURE_FILE


def main():
    price_df = load_prices(INPUT_PRICE_FILE)

    factory = FeatureFactory(price_df)
    features = factory.build_features()

    save_parquet(features, OUTPUT_FEATURE_FILE)

    print("✅ Feature Factory completed successfully")
    print(f"Output saved to: {OUTPUT_FEATURE_FILE}")


if __name__ == "__main__":
    main()
