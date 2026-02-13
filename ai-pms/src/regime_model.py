import pandas as pd
import numpy as np
from hmmlearn.hmm import GaussianHMM


class RegimeDetector:
    """
    Hidden‑Markov‑Model based regime detector.

    Produces:
    - daily regime probabilities
    - weekly confirmed regime state
    """

    def __init__(self, n_states: int = 3):
        self.n_states = n_states
        self.model = GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=200,
            random_state=42,
        )

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = ["ret_1d", "vol_20d", "mom_20_60"]
        return df[cols].dropna()

    def fit(self, df: pd.DataFrame):
        X = self._prepare_features(df).values
        self.model.fit(X)

    def predict_daily_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        X = self._prepare_features(df).values
        probs = self.model.predict_proba(X)

        prob_df = pd.DataFrame(
            probs,
            columns=[f"regime_{i}_prob" for i in range(self.n_states)],
        )

        prob_df["date"] = df.loc[prob_df.index, "date"].values
        return prob_df

    def weekly_confirmed_regime(self, prob_df: pd.DataFrame) -> pd.DataFrame:
        prob_df = prob_df.copy()
        prob_df["week"] = pd.to_datetime(prob_df["date"]).dt.to_period("W")

        weekly = (
            prob_df.groupby("week")
            .mean()
            .drop(columns=["date"])
        )

        weekly["confirmed_regime"] = weekly.idxmax(axis=1)
        return weekly.reset_index()
