import pandas as pd
from .config import RAW_DATA_DIR, START_DATE


REQUIRED_COLUMNS = {"date", "ticker", "close"}


def load_prices():
    files = list(RAW_DATA_DIR.glob("*.csv"))
    if not files:
        raise RuntimeError("No raw CSV files found in data/raw")

    df_list = []
    for f in files:
        df = pd.read_csv(f)
        if not REQUIRED_COLUMNS.issubset(df.columns):
            raise RuntimeError(f"Schema violation in {f.name}")

        df = df[["date", "ticker", "close"]].copy()
        df_list.append(df)

    df = pd.concat(df_list, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= START_DATE]

    return df.sort_values(["date", "ticker"]).reset_index(drop=True)
