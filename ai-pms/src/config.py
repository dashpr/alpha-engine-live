from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PRICE_FILE = BASE_DIR / "data/input/prices_live.json"
OUTPUT_FEATURE_FILE = BASE_DIR / "data/output/features.parquet"

ROLLING_WINDOWS = [5, 20, 60]
VOL_WINDOWS = [20, 60]
