from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "phase5_frozen" / "output"

START_DATE = "2010-01-01"
PORTFOLIO_SIZE = 15
REBAlANCE_FREQ = "W-FRI"
MIN_REBALANCE_WEIGHT_CHANGE = 0.02

BROKERAGE = 0.001
SLIPPAGE = 0.001
IMPACT = 0.0005

SEED = 42
