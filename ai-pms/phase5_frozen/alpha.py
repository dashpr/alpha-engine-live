import pandas as pd


def compute_alpha(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    momentum = 0.6 * df["ret_60d"] + 0.4 * df["ret_20d"]
    mean_rev = -df["ret_5d"] / df["vol_20d"]

    df["alpha_score"] = 0.5 * momentum.rank(pct=True) + 0.5 * mean_rev.rank(pct=True)

    return df
