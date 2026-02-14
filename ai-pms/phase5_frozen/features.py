import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["ret_5d"] = df.groupby("ticker")["close"].pct_change(5)
    df["ret_20d"] = df.groupby("ticker")["close"].pct_change(20)
    df["ret_60d"] = df.groupby("ticker")["close"].pct_change(60)

    df["vol_20d"] = (
        df.groupby("ticker")["close"]
        .pct_change()
        .rolling(20)
        .std()
        .reset_index(level=0, drop=True)
    )

    return df.dropna()
