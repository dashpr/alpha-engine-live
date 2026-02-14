import hashlib
from pathlib import Path
from .config import OUTPUT_DIR


def sha256_of_df(df):
    data = df.to_csv(index=False).encode()
    return hashlib.sha256(data).hexdigest()


def save_outputs(equity_curve):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    equity_path = OUTPUT_DIR / "equity_curve.csv"
    equity_curve.to_csv(equity_path, index=False)

    checksum = sha256_of_df(equity_curve)
    (OUTPUT_DIR / "equity_checksum.txt").write_text(checksum)
